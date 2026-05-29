import sys
import traceback
import logging

logging.basicConfig(level=logging.DEBUG, filename='test_llm.log', filemode='w')
sys.path.append('.')

from backend.rag.pipeline import answer

try:
    print("Testing pipeline...", file=sys.stderr)
    result = answer('What is the attendance policy?')
    print("Result:", result, file=sys.stderr)
except Exception as e:
    with open("error_trace.log", "w") as f:
        traceback.print_exc(file=f)
    print("Error saved to error_trace.log", file=sys.stderr)
