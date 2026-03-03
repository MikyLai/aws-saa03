# Phase 1 - MVP
gh issue create --title "Design PostgreSQL schema" --body "Create questions, choices, answers, attempts tables"
gh issue create --title "Build FastAPI base API" --body "CRUD for questions + random question endpoint"
gh issue create --title "Setup Docker Compose (DB + API + Web)" --body "All services up locally"
gh issue create --title "Build Next.js question page" --body "Display question + submit answer"

# Phase 2 - Study Topics
gh issue create --title "Study VPC / Subnet / NAT / IGW"
gh issue create --title "Study S3 (storage classes + policies)"
gh issue create --title "Study IAM (roles vs policies)"
gh issue create --title "Study ELB / ASG"
gh issue create --title "Study RDS Multi-AZ"
gh issue create --title "Study Route 53"
gh issue create --title "Study CloudFront"
gh issue create --title "Study KMS"

# Phase 3 - Advanced Features
gh issue create --title "Add tags + difficulty filter"
gh issue create --title "Add random 50-question mock mode"
gh issue create --title "Add attempt tracking (wrong question log)"
gh issue create --title "Add scoring statistics dashboard"

# Phase 4 - AWS Deployment
gh issue create --title "Create ECR repo"
gh issue create --title "Provision RDS PostgreSQL"
gh issue create --title "Deploy Backend to ECS Fargate"
gh issue create --title "Deploy Frontend to ECS"
gh issue create --title "Add ALB + Route53"
gh issue create --title "Add Secrets Manager integration"
gh issue create --title "Setup GitHub Actions CI/CD"

# Phase 5 - Exam Simulation
gh issue create --title "Full 50-question mock exam"
gh issue create --title "Analyze weak domains"
gh issue create --title "Final review + exam booking"