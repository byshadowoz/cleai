import transformers as tfr
import gc
import torch

def generate_code(prompt: str, model_name: str = "Salesforce/codegen-2B-multi") -> str:
    """
    Generate code based on a given prompt using a pre-trained model.

    Args:
        prompt (str): The input prompt to generate code from.
        model_name (str): The name of the pre-trained model to use.

    Returns:
        str: The generated code.
    """

    # Clear cache to free up memory
    gc.collect()
    torch.cuda.empty_cache()
    tokenizer = tfr.AutoTokenizer.from_pretrained(model_name)

    pipe = tfr.pipeline("code-generation", model=model_name, tokenizer=tokenizer)
    gen_c = pipe(prompt, num_return_sequences=1, max_length=512)[0]['generated_text']
    return gen_c

if __name__ == "__main__":
    # Example usage
    prompt = "Write a Python function to calculate the factorial of a number."

    generated_code = generate_code(prompt)
    print(generated_code)