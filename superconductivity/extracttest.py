import openai
import fitz 
import tiktoken

# create OpenAI client
client = openai.OpenAI(api_key="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")

# five key positions
positions = [
    "Electron pairing is mediated by magnetic (spin) fluctuations, not phonons.",
    "Non-s-wave pairing symmetry (e.g., d-wave) is a key feature of unconventional superconductivity.",
    "The pseudogap phase in cuprates plays a central role in high-Tc behavior.",
    "Unconventional superconductivity often emerges near quantum critical points.",
    "Topological superconductivity may arise from unconventional mechanisms."
]

# extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# count tokens
def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# estimate cost
def estimate_cost(input_tokens, output_tokens, model="gpt-4"):
    if model == "gpt-4":
        input_rate = 0.03 / 1000
        output_rate = 0.06 / 1000
    elif model == "gpt-3.5-turbo":
        input_rate = 0.0015
        output_rate = 0.002
    else:
        input_rate = output_rate = 0
    return round(input_tokens * input_rate + output_tokens * output_rate, 4)

# analyze paper with GPT
def analyze_paper_with_gpt(text):
    prompt = (
        "You are an expert in unconventional superconductivity. A student is studying papers beyond the BCS theory.\n\n"
        "Analyze the following paper in four parts:\n"
        
        "Important Instructions:\n"
        "- If a position is not explicitly discussed, score it 0/10 and write 'Not mentioned.'\n"
        "- Do not make inferences or assumptions. Only use content clearly stated in the paper.\n"
        "- Be strict and conservative in your scoring. High ratings require direct, unambiguous discussion.\n\n"

        "1. For each of the 5 positions below, rate how relevant this paper is on a scale from 1–10, with a brief reason.\n"
        "2. Give a short 3–5 sentence summary of the paper's main findings.\n"
        "3. Assess the paper’s credibility (authors, journal, experiment/theory, etc.).\n"
        "4. From the reference section of the paper, extract and list as many full citations as possible (e.g., authors, title, journal, year).\n"
        "If the reference section is missing or incomplete, do your best to list the cited works mentioned in the body of the text.\n\n"
        "Positions:\n"
        "1. Electron pairing is mediated by magnetic (spin) fluctuations, not phonons.\n"
        "2. Non-s-wave pairing symmetry (e.g., d-wave) is a key feature of unconventional superconductivity.\n"
        "3. The pseudogap phase in cuprates plays a central role in high-Tc behavior.\n"
        "4. Unconventional superconductivity often emerges near quantum critical points.\n"
        "5. Topological superconductivity may arise from unconventional mechanisms.\n\n"
        "Here is the paper:\n"
        + text[:12000]
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful physics research assistant."},

            # ONE-SHOT INPUT
            {"role": "user", "content":
                "The discovery of superfluidity in the 3He in 1971 by Osheroff, Richardson and Lee gave the first example of unconventional Cooper pairing. "
                "In 3He other pairing mechanisms are obviously of non-phononic origin, based on van der Waals and spin fluctuation mediated interactions. "
                "Moreover, 3He is the prime example for a strongly correlated Fermi liquid... "
                "In both types of material superconductivity emerges out of phases that are nearly magnetic or evolve under pressure from a magnetically ordered state. "
                "The essential role which magnetism could play for unconventional superconductivity became one of the guiding strategies in the nineties... "
                "superconductivity is associated with a quantum critical point of an antiferromagnetically ordered phase."
            },

            {"role": "assistant", "content":
                "1. Electron pairing is mediated by magnetic (spin) fluctuations, not phonons: 9/10. The text clearly states that 3He pairing is mediated by spin fluctuation interactions and that magnetism plays an essential role in other materials.\n"
                "2. Non-s-wave pairing symmetry (e.g., d-wave) is a key feature of unconventional superconductivity: 2/10. While unconventional pairing is mentioned, specific mention of non-s-wave or d-wave is absent.\n"
                "3. The pseudogap phase in cuprates plays a central role in high-Tc behavior: 0/10. Not mentioned.\n"
                "4. Unconventional superconductivity often emerges near quantum critical points: 8/10. The excerpt discusses superconductivity near antiferromagnetic quantum critical points, particularly in Ce-based compounds.\n"
                "5. Topological superconductivity may arise from unconventional mechanisms: 0/10. Not mentioned."
            },

            # ACTUAL TASK PROMPT
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1200
    )



    return response.choices[0].message.content, prompt

# run script
if __name__ == "__main__":
    file_path = "/Users/ericzhang/Desktop/Python_Projects/IntroUnSuper.pdf"
    paper_text = extract_text_from_pdf(file_path)
    result, prompt_used = analyze_paper_with_gpt(paper_text)

    input_tokens = count_tokens(prompt_used, model="gpt-4")
    output_tokens = count_tokens(result, model="gpt-4")
    cost = estimate_cost(input_tokens, output_tokens, model="gpt-4")

    print(f"\nInput tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Estimated cost: ${cost}")

    print("\n\n--- GPT Analysis ---\n")
    print(result)


