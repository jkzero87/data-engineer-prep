from ddgs import DDGS

results = DDGS().text("mejores raperos colombianos", max_results=3)
for r in results:
    print(r['title'])
    print(r['body'][:150])
    print('---')