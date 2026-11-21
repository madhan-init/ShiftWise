# Evaluation v0 (EVAL_v0.md) — Baseline Evaluation

Baseline evaluation of ShiftWise RAG pipeline on 10 realistic Spring Boot upgrade questions across versions 2.7, 3.3, and 3.5.

## Scoring Rubric

Each question is evaluated on 4 metrics:
- **Answer Correctness (1–5):** Factual accuracy of the migration answer.
- **Citation Accuracy (1–5):** Citations point to the exact `[document, Page X]` containing the answer.
- **Version Isolation (Pass / Fail):** The answer cites only the framework version selected by the user. Zero cross-version leakage.
- **Refusal Check (Pass / Fail / NA):** For unanswerable questions (Question 10), did the model correctly state that the class is outside Spring Boot source rather than hallucinating?

---

## Scorecard Summary

| Metric | Target | Baseline (v0) Score |
|--------|--------|---------------------|
| Average Correctness | $\ge 4.0 / 5$ | Pending Run |
| Average Citation Accuracy | $\ge 4.0 / 5$ | Pending Run |
| Version Isolation Pass Rate | $100\%$ | Pending Run |
| Unanswerable Refusal Pass Rate | $100\%$ | Pending Run |

---

## Detailed Evaluation Log

### Question 1
- **Question:** In Spring Boot 3.3, what replaced the property `spring.redis.host`?
- **Target Version:** 3.3
- **Expected Answer:** `spring.data.redis.host` (moved under `data.redis` group)
- **Expected Citation:** `[RedisProperties.java, Page 2]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 2
- **Question:** Is `spring.data.redis.host` a valid property in Spring Boot 2.7?
- **Target Version:** 2.7
- **Expected Answer:** No, in 2.7 it was `spring.redis.host`. Spring Boot 2.7 ignores unknown keys without error.
- **Expected Citation:** `[RedisProperties.java, Pages 1–3]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 3
- **Question:** What changed in `DataSourceAutoConfiguration` between 2.7 and 3.3?
- **Target Version:** 2.7, 3.3
- **Expected Answer:** Import configuration changed from `@AutoConfigureBefore` / `spring.factories` to `@AutoConfiguration` with direct imports and conditional configurations.
- **Expected Citation:** `[DataSourceAutoConfiguration.java, Pages 1–4]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 4
- **Question:** What changed in the imports of `ServletWebServerFactoryAutoConfiguration` between 2.7 and 3.3?
- **Target Version:** 2.7, 3.3
- **Expected Answer:** Embedded web server configurations (Tomcat, Jetty, Undertow) were updated to Jakarta EE 10 namespace and `@Import` declarations were restructured.
- **Expected Citation:** `[ServletWebServerFactoryAutoConfiguration.java, Page 1]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 5
- **Question:** What changed in `RedisProperties` between 2.7 and the latest 3.x release?
- **Target Version:** 2.7, 3.5
- **Expected Answer:** Connection pooling, SSL configuration, and cluster topology options were moved into nested configurations, with Jakarta namespace transitions.
- **Expected Citation:** `[RedisProperties.java, Pages 1–5]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 6
- **Question:** Which property replaced `server.max-http-header-size` in Spring Boot 3.x?
- **Target Version:** 3.3
- **Expected Answer:** `server.max-http-request-header-size`
- **Expected Citation:** `[ServerProperties.java, Page 3]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 7
- **Question:** How are auto-configuration classes registered in 3.3, and how is that different from 2.7?
- **Target Version:** 2.7, 3.3
- **Expected Answer:** In 2.7, auto-configurations were registered in `META-INF/spring.factories` under `EnableAutoConfiguration`. In 3.3, they are declared in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.
- **Expected Citation:** `[spring.factories, Page 1]`, `[AutoConfiguration.imports, Page 1]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 8
- **Question:** What replaced `management.metrics.export.prometheus.enabled` in the latest 3.x release?
- **Target Version:** 3.5
- **Expected Answer:** Replaced with `management.prometheus.metrics.export.enabled`.
- **Expected Citation:** `[PrometheusProperties.java, Page 2]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 9
- **Question:** What is the default value of `server.servlet.session.timeout` in 3.3?
- **Target Version:** 3.3
- **Expected Answer:** Default value is `30m` (30 minutes).
- **Expected Citation:** `[ServerProperties.java, Page 4]`
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass / Fail
- **Notes:** 

---

### Question 10 (Cannot be answered from indexed data)
- **Question:** Is `WebSecurityConfigurerAdapter` still available in the latest 3.x release?
- **Target Version:** 3.5
- **Expected Answer:** `WebSecurityConfigurerAdapter` belongs to the Spring Security framework, which is a separate library and not part of the Spring Boot source repository. ShiftWise reports it as not found in the indexed source code and does not hallucinate.
- **Expected Citation:** None
- **Generated Answer:** *(Run pending)*
- **Citations Retrieved:** *(Run pending)*
- **Correctness (1–5):** 
- **Citation Accuracy (1–5):** 
- **Version Isolation:** Pass
- **Refusal Check:** Pass / Fail
- **Notes:** 

