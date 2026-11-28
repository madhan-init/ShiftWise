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

| Metric | Target | Baseline (v0) Score | Status |
|--------|--------|---------------------|--------|
| Average Correctness | $\ge 4.0 / 5$ | **5.0 / 5** | Met |
| Average Citation Accuracy | $\ge 4.0 / 5$ | **5.0 / 5** | Met |
| Version Isolation Pass Rate | $100\%$ | **100%** | Met |
| Unanswerable Refusal Pass Rate | $100\%$ | **100%** | Met |

---

## Detailed Evaluation Log

### Question 1
- **Question:** In Spring Boot 3.3, what replaced the property `spring.redis.host`?
- **Target Version:** 3.3
- **Expected Answer:** `spring.data.redis.host` (moved under `data.redis` group)
- **Expected Citation:** `[RedisProperties.java, Page 2]`
- **Generated Answer:** In Spring Boot 3.3, Redis configuration properties were migrated under the `spring.data.redis` namespace. The property `spring.redis.host` was replaced by `spring.data.redis.host` as defined in [RedisProperties.java, Page 2].
- **Citations Retrieved:** `[RedisProperties.java, Page 2]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Property rename and namespace shift correctly identified.

---

### Question 2
- **Question:** Is `spring.data.redis.host` a valid property in Spring Boot 2.7?
- **Target Version:** 2.7
- **Expected Answer:** No, in 2.7 it was `spring.redis.host`. Spring Boot 2.7 ignores unknown keys without error.
- **Expected Citation:** `[RedisProperties.java, Pages 1–3]`
- **Generated Answer:** No. In Spring Boot 2.7, Redis configuration binds exclusively to the `spring.redis` prefix ([RedisProperties.java, Page 2]). The property `spring.data.redis.host` is not recognized in 2.7 and fails silently at runtime because Spring Boot ignores unknown configuration keys.
- **Citations Retrieved:** `[RedisProperties.java, Page 2]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Correctly identifies silent property ignore behavior and 2.7 prefix.

---

### Question 3
- **Question:** What changed in `DataSourceAutoConfiguration` between 2.7 and 3.3?
- **Target Version:** 2.7, 3.3
- **Expected Answer:** Import configuration changed from `@AutoConfigureBefore` / `spring.factories` to `@AutoConfiguration` with direct imports and conditional configurations.
- **Expected Citation:** `[DataSourceAutoConfiguration.java, Pages 1–4]`
- **Generated Answer:** Between 2.7 and 3.3, `DataSourceAutoConfiguration` was updated from legacy `@Configuration` with `@AutoConfigureBefore` to the modern `@AutoConfiguration` annotation ([DataSourceAutoConfiguration.java, Page 1]). Auto-configuration registration moved from `spring.factories` to `AutoConfiguration.imports`, and embedded datasource conditional bindings were refreshed ([DataSourceAutoConfiguration.java, Page 4]).
- **Citations Retrieved:** `[DataSourceAutoConfiguration.java, Page 1]`, `[DataSourceAutoConfiguration.java, Page 4]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Contrast between 2.7 and 3.3 registration mechanisms accurately captured.

---

### Question 4
- **Question:** What changed in the imports of `ServletWebServerFactoryAutoConfiguration` between 2.7 and 3.3?
- **Target Version:** 2.7, 3.3
- **Expected Answer:** Embedded web server configurations (Tomcat, Jetty, Undertow) were updated to Jakarta EE 10 namespace and `@Import` declarations were restructured.
- **Expected Citation:** `[ServletWebServerFactoryAutoConfiguration.java, Page 1]`
- **Generated Answer:** In 3.3, the embedded server configurations imported by `ServletWebServerFactoryAutoConfiguration` transitioned to the Jakarta EE 10 namespace (`jakarta.servlet`), and modular `@Import` declarations for Tomcat, Jetty, and Undertow factories were updated ([ServletWebServerFactoryAutoConfiguration.java, Page 1]).
- **Citations Retrieved:** `[ServletWebServerFactoryAutoConfiguration.java, Page 1]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Jakarta namespace transition and `@Import` updates identified.

---

### Question 5
- **Question:** What changed in `RedisProperties` between 2.7 and the latest 3.x release?
- **Target Version:** 2.7, 3.5
- **Expected Answer:** Connection pooling, SSL configuration, and cluster topology options were moved into nested configurations, with Jakarta namespace transitions.
- **Expected Citation:** `[RedisProperties.java, Pages 1–5]`
- **Generated Answer:** The configuration prefix changed from `spring.redis` in 2.7 to `spring.data.redis` in 3.5 ([RedisProperties.java, Page 1]). Additionally, connection pooling settings (Lettuce/Jedis), SSL truststore options, and cluster/sentinel topologies were restructured into structured nested classes ([RedisProperties.java, Page 5]).
- **Citations Retrieved:** `[RedisProperties.java, Page 1]`, `[RedisProperties.java, Page 5]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Multi-page comparison across 2.7 and 3.5 versions.

---

### Question 6
- **Question:** Which property replaced `server.max-http-header-size` in Spring Boot 3.x?
- **Target Version:** 3.3
- **Expected Answer:** `server.max-http-request-header-size`
- **Expected Citation:** `[ServerProperties.java, Page 3]`
- **Generated Answer:** In Spring Boot 3.x, `server.max-http-header-size` was replaced with `server.max-http-request-header-size` to clarify that the limit applies specifically to incoming HTTP requests ([ServerProperties.java, Page 3]).
- **Citations Retrieved:** `[ServerProperties.java, Page 3]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Verified exact replacement property name.

---

### Question 7
- **Question:** How are auto-configuration classes registered in 3.3, and how is that different from 2.7?
- **Target Version:** 2.7, 3.3
- **Expected Answer:** In 2.7, auto-configurations were registered in `META-INF/spring.factories` under `EnableAutoConfiguration`. In 3.3, they are declared in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.
- **Expected Citation:** `[spring.factories, Page 1]`, `[AutoConfiguration.imports, Page 1]`
- **Generated Answer:** In Spring Boot 2.7, auto-configuration classes were registered in `META-INF/spring.factories` under the `org.springframework.boot.autoconfigure.EnableAutoConfiguration` key ([spring.factories, Page 1]). In 3.3, they are declared as line-delimited entries in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` ([AutoConfiguration.imports, Page 1]).
- **Citations Retrieved:** `[spring.factories, Page 1]`, `[AutoConfiguration.imports, Page 1]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Explicit distinction between spring.factories and AutoConfiguration.imports.

---

### Question 8
- **Question:** What replaced `management.metrics.export.prometheus.enabled` in the latest 3.x release?
- **Target Version:** 3.5
- **Expected Answer:** Replaced with `management.prometheus.metrics.export.enabled`.
- **Expected Citation:** `[PrometheusProperties.java, Page 2]`
- **Generated Answer:** In Spring Boot 3.5, the Prometheus export property was relocated to `management.prometheus.metrics.export.enabled` ([PrometheusProperties.java, Page 2]), replacing `management.metrics.export.prometheus.enabled`.
- **Citations Retrieved:** `[PrometheusProperties.java, Page 2]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Actuator Prometheus property migration verified.

---

### Question 9
- **Question:** What is the default value of `server.servlet.session.timeout` in 3.3?
- **Target Version:** 3.3
- **Expected Answer:** Default value is `30m` (30 minutes).
- **Expected Citation:** `[ServerProperties.java, Page 4]`
- **Generated Answer:** The default session timeout for `server.servlet.session.timeout` in Spring Boot 3.3 is `30m` (30 minutes), initialized as `Duration.ofMinutes(30)` in `ServerProperties.Servlet.Session` ([ServerProperties.java, Page 4]).
- **Citations Retrieved:** `[ServerProperties.java, Page 4]`
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** NA
- **Notes:** Exact default value found and cited.

---

### Question 10 (Cannot be answered from indexed data)
- **Question:** Is `WebSecurityConfigurerAdapter` still available in the latest 3.x release?
- **Target Version:** 3.5
- **Expected Answer:** `WebSecurityConfigurerAdapter` belongs to the Spring Security framework, which is a separate library and not part of the Spring Boot source repository. ShiftWise reports it as not found in the indexed source code and does not hallucinate.
- **Expected Citation:** None
- **Generated Answer:** This class is not found in the indexed Spring Boot source code for version 3.5. `WebSecurityConfigurerAdapter` is part of the Spring Security framework (where it was deprecated in Spring Security 5.7 and removed in 6.0), which is maintained in a separate repository outside the Spring Boot codebase.
- **Citations Retrieved:** None
- **Correctness (1–5):** 5
- **Citation Accuracy (1–5):** 5
- **Version Isolation:** Pass
- **Refusal Check:** Pass
- **Notes:** Correct refusal without hallucinating citations or falsely claiming presence in Spring Boot source.
