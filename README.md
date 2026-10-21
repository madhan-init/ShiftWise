# ShiftWise

## Problem
Many Indian services companies still run old Spring Boot versions and are now upgrading to 3.x. Developers mix up advice written for 2.7 and 3.x, and renamed properties fail silently at runtime because Spring ignores unknown keys. There is no reliable list of what changed in the code between versions, so problems show up late in testing or production. ShiftWise answers every question using only the Spring Boot source code of the version the developer selects, and shows exactly what changed between two versions. It also reviews upgrade pull requests and comments with cited fixes.

## Who it is for
- Senior Java developer at an insurance software services firm in Chennai, upgrading 12 client apps from Spring Boot 2.7 to 3.x.
- Tech lead at the same firm, who approves each upgrade pull request review before it is posted to GitHub.

## Signature feature
A version switch that locks every answer and citation to one Spring Boot release, with a diff button that shows the old and new code side by side.

## Hardest problem (my interview story)
The hardest problem is making sure an answer never cites code from the wrong version. Classes and properties with the same name exist in 2.7, 3.3 and the latest 3.x release, so a normal search can easily return the wrong one, and an instruction in the prompt cannot guarantee otherwise. My solution is to tag every chunk with its release version, filter retrieval by the selected version, and check every citation against the retrieved chunks before showing the answer. I measure this with an 80-question test set where the target is zero wrong-version citations.

## Dataset
| Source | Link | Documents | Pages | Licence / terms |
|---|---|---|---|---|
| Spring Boot source code (release tags 2.7.x, 3.3.x, latest 3.x) | https://github.com/spring-projects/spring-boot | 9,000+ source files per version, 3 versions | Not applicable (source code files) | Apache-2.0 |

## 10 real questions
See [docs/QUESTIONS.md](docs/QUESTIONS.md).

## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
curl localhost:8000/health
```

## Live link
Added in Week 2