from dotenv import load_dotenv
import os
import sys
import io
import ast
from llama_index.experimental.query_engine import PandasQueryEngine
from prompts import new_prompt, instruction_str, context
from data import df
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
import time
from llama_index.core.memory import ChatMemoryBuffer
import matplotlib.pyplot as plt
import pandas as pd


import google.generativeai as genai

load_dotenv()
# Configure Gemini 
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from llama_index.core import Settings
Settings.llm = Gemini(model="gemini-2.5-flash-lite")


def python_repl(code: str):
    """Executes Python code and returns structured output including final_answer"""
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    try:
        plt.switch_backend('Agg')
        local_vars = {}
        exec(code, {'pd': pd, 'plt': plt, 'df': df, **globals()}, local_vars)
        output = buffer.getvalue().strip()
        
        # Capture the last expression's value
        result = local_vars.get('_', None)
        
        # Handle visualization
        image_path = None
        if plt.get_fignums():
            image_filename = f"plot_{int(time.time())}.png"
            image_path = f"generated_images/{image_filename}"
            plt.savefig(image_path, bbox_inches='tight', dpi=100)
            plt.close()
        
        # The final answer content
        if output:
            final_answer = output
        elif result is not None:
            final_answer = str(result)
        else:
            final_answer = "Code executed successfully (no output)"
        
        
        return {
            "code": code,
            "output": output,
            "result": str(result) if result is not None else None,
            "image_path": image_path,
            "final_answer": final_answer,
            "is_final": True
        }
            
    except Exception as e:
        return {
            "code": code,
            "error": str(e),
            "final_answer": f"Error: {str(e)}",
            "is_final": False
        }
    finally:
        sys.stdout = old_stdout
        plt.close('all')
        
repl_tool = FunctionTool.from_defaults(
    fn=python_repl,
    name="python_repl",
    description=f"""Execute Python code to analyze air quality data. Follow these instructions:
    {instruction_str}
    
    Available data:
    - DataFrame 'df' with columns: timestamp, room, temperature, humidity, co2
    - Pre-imported libraries: pandas (pd), matplotlib.pyplot (plt)
    
    Always:
    - Normalize room names according to instructions
    - Include units in responses
    - Handle errors gracefully
    - For visualizations, include plt.show()
    """
)


memory = ChatMemoryBuffer.from_defaults(token_limit=4000)


agent = ReActAgent.from_tools(
    [repl_tool], 
    llm=Settings.llm, 
    memory=memory,
    verbose=True,
    context=context,
    system_prompt=new_prompt
)

