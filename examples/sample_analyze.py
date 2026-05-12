"""Contoh pakai analyzer secara programmatic."""
from pushfyp import analyzer

url = "https://www.threads.net/@zuck/post/C5abcDefGhi"
result = analyzer.analyze(url)

print(f"Score: {result.score}/100")
print("Suggestions:")
for s in result.suggestions:
    print(f"  - {s}")
