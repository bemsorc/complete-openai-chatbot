from openai import OpenAI

openai = OpenAI(
    api_key = "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"
)

response = openai.images.generate(
    prompt="cartoon duck with eye glasses",
    n=1,
    size="512x512")

print(response.data[0].url)