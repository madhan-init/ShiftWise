# ShiftWise
Answers for the exact framework version you run, plus a clear list of what changed between versions.
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
# 10 Real Questions

These are the questions a developer upgrading Spring Boot 2.7 apps to 3.x would ask ShiftWise. Each question is answered only from the Spring Boot source code of the version named in the question.

| # | Question | Version(s) | Type |
|---|---|---|---|
| 1 | In Spring Boot 3.3, what replaced the property `spring.redis.host`? | 3.3 | Property rename |
| 2 | Is `spring.data.redis.host` a valid property in Spring Boot 2.7? | 2.7 | Wrong-version check |
| 3 | What changed in `DataSourceAutoConfiguration` between 2.7 and 3.3? | 2.7, 3.3 | What changed |
| 4 | What changed in the imports of `ServletWebServerFactoryAutoConfiguration` between 2.7 and 3.3? | 2.7, 3.3 | What changed |
| 5 | What changed in `RedisProperties` between 2.7 and the latest 3.x release? | 2.7, 3.5 | What changed |
| 6 | Which property replaced `server.max-http-header-size` in Spring Boot 3.x? | 3.3 | Property rename |
| 7 | How are auto-configuration classes registered in 3.3, and how is that different from 2.7? | 2.7, 3.3 | What changed |
| 8 | What replaced `management.metrics.export.prometheus.enabled` in the latest 3.x release? | 3.5 | Property rename |
| 9 | What is the default value of `server.servlet.session.timeout` in 3.3? | 3.3 | Default value lookup |
| 10 | Is `WebSecurityConfigurerAdapter` still available in the latest 3.x release? | 3.5 | Cannot be answered from the documents |

## Question the documents cannot answer

Question 10 cannot be answered from the indexed data. `WebSecurityConfigurerAdapter` belongs to Spring Security, which is a separate project and is not part of the Spring Boot repository. The expected behaviour is that ShiftWise states that the class is not found in the indexed Spring Boot source for the selected version, and does not guess.

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
