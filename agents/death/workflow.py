import os
import logging
from typing import TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from db.database import add_citizen, add_informant, add_death_record, get_citizen_by_id
from agents.death.tools import check_duplicate_death, verify_document, generate_certificate
from .embeddings import query_embeddings
from .config import DOCUMENTS_PATH
from .llm import groq_llm_reason  # LLM wrapper

# --------------------------
# Logging Setup
# --------------------------
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbose
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --------------------------
# State Type
# --------------------------
class DeathRegistrationState(TypedDict):
    citizen_id: int
    national_id: str
    full_name: str
    gender: str
    dob: datetime
    date_of_death: datetime
    place_of_death: str
    cause_of_death: str
    informant_name: str
    informant_id: str
    relation: str
    uploaded_files: list
    documents_verified: bool
    status: str
    certificate_number: str
    certificate_path: str
    record_id: int

# --------------------------
# Node Functions
# --------------------------
def collect_citizen_data(state: dict) -> dict:
    logger.info("=== Collecting Citizen Data ===")
    citizen = get_citizen_by_id(state['national_id'])
    if citizen:
        state['citizen_id'] = citizen[0]
        logger.info(f"Citizen already exists: {state['citizen_id']}")
    else:
        state['citizen_id'] = add_citizen(
            state['full_name'], state['national_id'], state['gender'], state['dob']
        )
        logger.info(f"New citizen added: {state['citizen_id']}")

    state['informant_id'] = add_informant(
        state['informant_name'], state['informant_id'], state['relation']
    )
    logger.info(f"Informant added: {state['informant_id']}")
    return state

def collect_documents(state: dict) -> dict:
    logger.info("=== Collecting and Verifying Documents ===")
    os.makedirs(DOCUMENTS_PATH, exist_ok=True)
    verified_docs = []

    for file_obj in state.get('uploaded_files', []):
        file_path = os.path.join(DOCUMENTS_PATH, file_obj.name)
        with open(file_path, "wb") as f:
            f.write(file_obj.getbuffer())
        logger.info(f"Saved uploaded file: {file_obj.name}")

        # OCR verification
        ocr_verified = verify_document(file_path, required_keywords=[state['national_id']])
        logger.info(f"OCR verification for {file_obj.name}: {ocr_verified}")

        # LLM assisted reasoning with embeddings
        kb_context = query_embeddings("Required documents for death registration")
        llm_prompt = f"""
        You are an AI agent assisting with death registration.
        OCR verified: {ocr_verified}.
        Uploaded file: {file_obj.name}.
        Knowledge base context: {kb_context}.
        Citizen: {state['full_name']} ({state['national_id']}).
        Decide if this document is valid for registration (return True/False).
        """
        llm_decision = groq_llm_reason(llm_prompt).lower() in ['true', 'yes', 'approved']
        logger.info(f"LLM decision for {file_obj.name}: {llm_decision}")

        verified_docs.append({
            "file_name": file_obj.name,
            "file_path": file_path,
            "verified": ocr_verified and llm_decision
        })

    state['documents'] = verified_docs
    state['documents_verified'] = all(doc['verified'] for doc in verified_docs)
    logger.info(f"All documents verified: {state['documents_verified']}")
    return state

def fraud_check(state: dict) -> dict:
    logger.info("=== Performing Fraud Check ===")
    duplicate_check = check_duplicate_death(state['citizen_id'])
    kb_context = query_embeddings("Fraud checks for death registration")
    llm_prompt = f"""
    You are an AI agent for fraud detection in death registration.
    Citizen ID: {state['citizen_id']}.
    Duplicate check result: {duplicate_check}.
    Documents verified: {state.get('documents_verified')}.
    Knowledge base: {kb_context}.
    Decide the registration status: approved, rejected_duplicate, or rejected_fraud.
    """
    decision = groq_llm_reason(llm_prompt).strip().lower()
    if decision not in ['approved', 'rejected_duplicate', 'rejected_fraud']:
        decision = 'rejected_duplicate' if duplicate_check else 'approved'
    state['status'] = decision
    logger.info(f"Fraud check decision: {decision}")
    return state

def db_insert(state: dict) -> dict:
    logger.info("=== Inserting into Database ===")
    if state.get('status') == 'approved':
        record_id = add_death_record(
            citizen_id=state['citizen_id'],
            date_of_death=state['date_of_death'],
            place=state['place_of_death'],
            cause=state['cause_of_death'],
            informant_id=state['informant_id'],
            certificate_number=None
        )
        state['record_id'] = record_id
        logger.info(f"Death record added: {record_id}")
    return state

def certificate_gen(state: dict) -> dict:
    logger.info("=== Generating Certificate ===")
    if state.get('status') == 'approved' and state.get('record_id'):
        death_record = {
            "record_id": state['record_id'],
            "full_name": state['full_name'],
            "national_id": state['national_id'],
            "date_of_death": state['date_of_death'],
            "place_of_death": state['place_of_death'],
            "cause_of_death": state['cause_of_death'],
            "informant_name": state['informant_name']
        }
        file_path, cert_num = generate_certificate(death_record)
        state['certificate_number'] = cert_num
        state['certificate_path'] = file_path
        logger.info(f"Certificate generated at: {file_path} (Number: {cert_num})")
    else:
        # Hackathon/mock fallback
        state['certificate_number'] = "MOCK-0001"
        state['certificate_path'] = f"certificates/mock_certificate_{state.get('record_id', '0000')}.pdf"
        logger.info(f"Mock certificate path set: {state['certificate_path']}")
    return state

# --------------------------
# Build Graph
# --------------------------
death_graph = StateGraph(DeathRegistrationState)
death_graph.add_node("collect_citizen_data", collect_citizen_data)
death_graph.add_node("collect_documents", collect_documents)
death_graph.add_node("fraud_check", fraud_check)
death_graph.add_node("db_insert", db_insert)
death_graph.add_node("certificate_gen", certificate_gen)

death_graph.add_edge(START, "collect_citizen_data")
death_graph.add_edge("collect_citizen_data", "collect_documents")
death_graph.add_edge("collect_documents", "fraud_check")
death_graph.add_edge("fraud_check", "db_insert")
death_graph.add_edge("db_insert", "certificate_gen")
death_graph.add_edge("certificate_gen", END)

compiled_graph = death_graph.compile()

# --------------------------
# Runner Function
# --------------------------
def run_death_registration(initial_state: dict) -> dict:
    logger.info("=== Starting Death Registration Workflow ===")
    final_state = compiled_graph.invoke(initial_state)
    logger.info(f"=== Workflow Finished. Final state: {final_state} ===")
    return final_state
