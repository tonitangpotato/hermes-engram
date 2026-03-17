"""Generate a mock Engram DB with realistic AI agent memories."""
import sqlite3
import random
import hashlib
import time
import os

DB_PATH = os.path.expanduser("~/clawd/projects/agent-memory-prototype/pensieve/mock-engram.db")

# Remove existing
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Schema from Engram
c.executescript("""
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    summary TEXT,
    tokens INTEGER DEFAULT 0,
    memory_type TEXT DEFAULT 'semantic',
    layer TEXT DEFAULT 'working',
    created_at REAL DEFAULT (strftime('%s', 'now')),
    working_strength REAL DEFAULT 1.0,
    core_strength REAL DEFAULT 0.0,
    importance REAL DEFAULT 0.5,
    pinned INTEGER DEFAULT 0,
    consolidation_count INTEGER DEFAULT 0,
    last_consolidated REAL,
    source_file TEXT,
    contradicts TEXT,
    contradicted_by TEXT,
    namespace TEXT DEFAULT 'default'
);

CREATE TABLE IF NOT EXISTS access_log (
    memory_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    accessed_at REAL DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS hebbian_links (
    source_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    target_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    strength REAL DEFAULT 1.0,
    coactivation_count INTEGER DEFAULT 0,
    created_at REAL DEFAULT (strftime('%s', 'now')),
    PRIMARY KEY (source_id, target_id)
);

CREATE TABLE IF NOT EXISTS graph_links (
    memory_id TEXT,
    node_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_access_log_mid ON access_log(memory_id);
CREATE INDEX IF NOT EXISTS idx_hebbian_source ON hebbian_links(source_id);
CREATE INDEX IF NOT EXISTS idx_hebbian_target ON hebbian_links(target_id);
CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);
""")

now = time.time()
DAY = 86400

# Memory templates by type
FACTUAL = [
    "User's main project is a Rust web API using Axum + SQLx + PostgreSQL",
    "Production database runs on PostgreSQL 16 with pgvector extension",
    "CI/CD pipeline uses GitHub Actions with Docker builds",
    "Deployment target is AWS ECS Fargate with ALB",
    "User prefers vim keybindings in VS Code",
    "Project uses trunk-based development with short-lived feature branches",
    "Test suite runs with cargo test and includes integration tests against test DB",
    "User's timezone is America/Los_Angeles, prefers async communication",
    "API rate limiting implemented via Redis with sliding window algorithm",
    "Monitoring stack: Prometheus + Grafana + AlertManager",
    "User runs macOS 14 Sonoma with Homebrew package manager",
    "Docker Desktop and Podman both installed, prefers Podman for production",
    "SSH config uses ed25519 keys, staging server on port 2222",
    "Python projects use uv for dependency management instead of pip",
    "Terraform manages all AWS infrastructure, state in S3 backend",
    "User has 3 microservices: auth-service, data-pipeline, api-gateway",
    "GraphQL API uses async-graphql crate with DataLoader pattern",
    "Background jobs processed by Tokio tasks with graceful shutdown",
    "User prefers concise responses, dislikes verbose explanations",
    "Error handling follows RFC 7807 Problem Details standard",
    "Database migrations managed by sqlx-cli with reversible migrations",
    "Redis used for caching (TTL 5min), sessions (TTL 24h), and rate limiting",
    "Logging uses tracing crate with JSON output for structured logs",
    "User's laptop is M2 MacBook Pro 16GB, build times ~45s for full rebuild",
    "API authentication uses JWT with RS256, refresh tokens in httpOnly cookies",
    "Frontend is Next.js 14 with App Router, deployed on Vercel",
    "WebSocket connections handled by axum::extract::ws with heartbeat",
    "User has ADHD, works best in 25-min pomodoro sprints",
    "Preferred code review style: focus on architecture, not formatting",
    "Team standup at 10am PT daily, async updates in Slack #engineering",
    "Load testing with k6, target: 1000 RPS at p99 < 200ms",
    "Feature flags managed by LaunchDarkly SDK",
    "User allergic to peanuts — critical safety information",
    "Payment processing via Stripe, webhook signature verification required",
    "S3 bucket naming convention: {env}-{service}-{purpose}",
    "Database connection pool: min=5, max=20, timeout=30s",
    "User prefers dark mode in all applications",
    "Git commit messages follow Conventional Commits spec",
    "API versioning via URL path (/v1/, /v2/) not headers",
    "Kubernetes cluster on EKS with 3 node groups (system, app, data)",
    "User speaks English and Mandarin, technical discussions in English",
    "OpenTelemetry tracing configured with Jaeger backend",
    "Cache invalidation strategy: event-driven via Redis pub/sub",
    "User's dog is named Luna, a golden retriever",
    "Backup strategy: daily DB snapshots retained 30 days, WAL archiving to S3",
    "gRPC used for inter-service communication, protobuf schemas in shared repo",
    "User prefers functional programming patterns over OOP",
    "Memory limit per container: 512MB for API, 2GB for data pipeline",
    "User drinks oat milk lattes, relevant for coffee order context",
    "SSL certificates managed by cert-manager with Let's Encrypt",
]

EPISODIC = [
    "Debugged a memory leak in the WebSocket handler — caused by unbounded channel buffer",
    "Migrated from MySQL to PostgreSQL on 2025-11-15, took 3 days",
    "Production outage on Dec 3: Redis connection pool exhaustion during Black Friday traffic",
    "Successfully load tested to 5000 RPS after connection pooling optimization",
    "Pair programmed with Sarah on the auth refactor — she suggested the refresh token rotation pattern",
    "User got frustrated when I suggested using ORM instead of raw SQL — noted preference",
    "Deployed v2.0 of the API gateway, zero-downtime migration completed",
    "Spent 2 hours debugging CORS issues — turned out to be a missing header in the preflight response",
    "User praised the Terraform module I helped organize — said it was the cleanest IaC they'd seen",
    "Rolled back deployment on Jan 8 due to breaking change in serialization format",
    "User mentioned burnout concerns — suggested breaking large tasks into smaller PRs",
    "Fixed N+1 query in the user dashboard endpoint — response time dropped from 2.3s to 180ms",
    "User's birthday is March 15 — they mentioned it during a casual conversation",
    "Team retrospective revealed need for better error messages in API responses",
    "First successful canary deployment using Argo Rollouts",
    "User stayed up until 3am fixing a data corruption bug in the pipeline",
    "Helped user prepare for system design interview — practiced designing a URL shortener",
    "User switched from iTerm2 to Warp terminal — likes the AI command suggestions",
    "Database schema redesign meeting — decided to denormalize the analytics tables",
    "User got promoted to Senior Engineer in February — congratulated them",
]

PROCEDURAL = [
    "To deploy to staging: git push origin staging → GitHub Actions builds → ECS deploys automatically",
    "Database migration workflow: create migration with sqlx migrate add, test locally, PR review, deploy",
    "When Redis is down: API falls back to database queries with 1-minute cache in process memory",
    "Debugging production issues: check Grafana dashboards first, then CloudWatch logs, then SSH if needed",
    "To rotate API keys: generate new key in AWS Secrets Manager, deploy, verify, revoke old key",
    "Performance profiling: use cargo flamegraph for CPU, heaptrack for memory, tokio-console for async",
    "When tests fail on CI but pass locally: check for time-dependent tests and parallel execution conflicts",
    "SSL cert renewal process: cert-manager handles automatically, but verify with kubectl get certificates",
    "To add a new microservice: copy template repo, update Terraform, add to API gateway routes",
    "Incident response: acknowledge in PagerDuty → investigate → mitigate → post-mortem within 48h",
    "Code review checklist: security, performance, error handling, tests, documentation",
    "To set up local dev: clone repo, cp .env.example .env, docker compose up, cargo run",
    "When memory usage spikes: check for large query results not being streamed, connection leaks",
    "Blue-green deployment: update inactive target group, run smoke tests, swap ALB listener",
    "To generate API docs: cargo doc --open for Rust, swagger-ui for REST endpoints",
]

CAUSAL = [
    "Increasing connection pool size from 10 to 20 reduced p99 latency by 40% under load",
    "Adding database indexes on user_id + created_at eliminated slow dashboard queries",
    "Switching from synchronous to async file uploads improved throughput by 3x",
    "Redis connection pool exhaustion caused cascading failures across all services",
    "Enabling HTTP/2 on the load balancer reduced time-to-first-byte by 25%",
    "Batch inserts instead of individual inserts reduced data pipeline runtime from 45min to 8min",
    "Adding circuit breaker to external API calls prevented cascade failures during partner outage",
    "Removing unnecessary clone() calls in hot path reduced memory allocation by 60%",
    "Enabling compression on API responses reduced bandwidth costs by 70%",
    "Switching from polling to WebSocket for real-time updates reduced server CPU by 40%",
    "Adding retry logic with exponential backoff fixed intermittent S3 upload failures",
    "Denormalizing the analytics table eliminated 12 JOIN operations and 10x query speed",
    "Moving image processing to Lambda reduced API server memory usage by 500MB",
    "Implementing request coalescing reduced duplicate database queries by 80%",
    "Adding structured logging made debugging production issues 5x faster",
]

RELATIONAL = [
    "Sarah — team lead, prefers detailed PR descriptions, good at system design",
    "Mike — DevOps lead, manages Kubernetes cluster, timezone UTC+0",
    "The data-pipeline service depends on auth-service for token validation",
    "PostgreSQL and Redis are the two critical infrastructure dependencies",
    "Next.js frontend communicates with Rust API via GraphQL and REST",
    "Stripe webhooks must be processed within 30 seconds or they retry",
    "User's manager is Alex — supportive of technical improvements",
    "CI pipeline depends on Docker Hub for base images — had outage when Docker Hub was down",
    "The analytics dashboard queries both PostgreSQL and ClickHouse",
    "User's preferred learning resources: Rust by Example, Tokio docs, Alex Xu's system design book",
    "Luna (dog) needs walking at 6pm — user often wraps up work around 5:45pm",
    "User's partner works in healthcare, often discusses AI applications in medicine",
    "Auth-service is the most critical service — if it goes down, everything fails",
    "User collaborates with data science team on the recommendation engine",
    "Team uses Notion for documentation, Linear for issue tracking",
]

all_memories = []
mem_ids = []

def make_id():
    return hashlib.md5(str(random.random()).encode()).hexdigest()[:8]

# Generate memories with realistic timestamps and strengths
types_and_data = [
    ("factual", FACTUAL),
    ("episodic", EPISODIC),
    ("procedural", PROCEDURAL),
    ("causal", CAUSAL),
    ("relational", RELATIONAL),
]

for mem_type, templates in types_and_data:
    for content in templates:
        mid = make_id()
        mem_ids.append(mid)
        
        age_days = random.uniform(0, 30)
        created = now - age_days * DAY
        
        # Working strength decays with age
        working = max(0.01, 1.0 * (0.5 ** (age_days / 7)))
        # Core strength grows with consolidation
        consolidation = random.randint(0, 10)
        core = min(1.0, consolidation * 0.1)
        importance = random.uniform(0.2, 0.95)
        
        layer = "core" if core > 0.5 else "working"
        
        c.execute("""
            INSERT INTO memories (id, content, memory_type, layer, created_at,
                working_strength, core_strength, importance, consolidation_count, namespace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'default')
        """, (mid, content, mem_type, layer, created, working, core, importance, consolidation))
        
        # Generate access log entries
        num_accesses = random.randint(1, 50)
        for _ in range(num_accesses):
            access_time = created + random.uniform(0, age_days * DAY)
            c.execute("INSERT INTO access_log (memory_id, accessed_at) VALUES (?, ?)",
                      (mid, access_time))

# Generate Hebbian links between related memories
print(f"Generated {len(mem_ids)} memories")

# Create meaningful links: memories of similar types or related content
link_count = 0
for i in range(len(mem_ids)):
    # Each memory links to 2-6 others
    num_links = random.randint(2, 6)
    targets = random.sample(mem_ids, min(num_links, len(mem_ids)))
    for target in targets:
        if target != mem_ids[i]:
            strength = random.uniform(0.1, 1.0)
            coactivation = random.randint(1, 15)
            try:
                c.execute("""
                    INSERT OR IGNORE INTO hebbian_links 
                    (source_id, target_id, strength, coactivation_count, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (mem_ids[i], target, strength, coactivation, now - random.uniform(0, 20) * DAY))
                link_count += 1
            except:
                pass

conn.commit()

# Print stats
total_mems = c.execute("SELECT count(*) FROM memories").fetchone()[0]
total_links = c.execute("SELECT count(*) FROM hebbian_links").fetchone()[0]
total_accesses = c.execute("SELECT count(*) FROM access_log").fetchone()[0]
types = c.execute("SELECT memory_type, count(*) FROM memories GROUP BY memory_type").fetchall()

print(f"\nMock Engram DB: {DB_PATH}")
print(f"  Memories: {total_mems}")
print(f"  Hebbian links: {total_links}")
print(f"  Access log entries: {total_accesses}")
print(f"  Types: {dict(types)}")

conn.close()
