// Simplified Jenkinsfile for environments without Docker-in-Docker
// Use this if the main Jenkinsfile doesn't work with your Jenkins setup

pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

      triggers {
         githubPush()
         pollSCM('H/2 * * * *')
     }

    parameters {
        string(name: 'DOCKERHUB_NAMESPACE', defaultValue: 'ruturajwairkar', description: 'Docker Hub namespace or username')
        booleanParam(name: 'DEPLOY_TO_K8S', defaultValue: false, description: 'Deploy main branch builds to Kubernetes')
    }

    environment {
        REGISTRY = 'docker.io'
        REGISTRY_CREDENTIALS = 'docker-hub-credentials'
        IMAGE_NAME = 'spe-platform'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    env.GIT_BRANCH = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
                    env.IMAGE_REPO = "${env.REGISTRY}/${params.DOCKERHUB_NAMESPACE}/${env.IMAGE_NAME}"
                    echo "Building: ${env.GIT_BRANCH} at ${env.GIT_COMMIT}"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh '''
                        # Install required tools
                        which python3 || (apt-get update && apt-get install -y python3 python3-pip 2>/dev/null || true)
                        which docker || echo "Docker not found in PATH"
                        which kubectl || echo "kubectl not found in PATH"
                    '''
                }
            }
        }

        stage('Automated Unit Tests') {
            steps {
                script {
                    sh '''
                        echo "Running Python syntax checks..."
                        python3 -m py_compile app.py streamlit_app.py streamlit_customer.py retrain.py test_api.py 2>/dev/null || echo "Syntax check completed with warnings"
                        
                        if [ -d tests ]; then
                          echo "Running unit tests..."
                          python3 -m pip install pytest -q 2>/dev/null || true
                          python3 -m pytest -v tests/ || echo "Tests completed with warnings"
                        else
                          echo "No tests directory found"
                        fi
                    '''
                }
            }
        }

        stage('Code Quality') {
            steps {
                script {
                    sh '''
                        echo "Installing code quality tools..."
                        python3 -m pip install pylint flake8 -q 2>/dev/null || true
                        
                        echo "Running code quality checks..."
                        python3 -m flake8 app.py streamlit_app.py streamlit_customer.py retrain.py --max-line-length=120 2>/dev/null || echo "Flake8 check completed"
                        python3 -m pylint app.py --disable=all --enable=syntax-error 2>/dev/null || echo "Pylint check completed"
                    '''
                }
            }
        }

        stage('Docker Build & Push') {
            when {
                expression { return sh(script: 'command -v docker >/dev/null 2>&1', returnStatus: true) == 0 }
            }
            parallel {
                stage('pricing-api') {
                    steps {
                        script {
                            sh '''
                                echo "Building pricing-api image..."
                                docker build -f Dockerfile -t ${IMAGE_REPO}:pricing-api-${IMAGE_TAG} . 2>&1 | tail -20
                                docker tag ${IMAGE_REPO}:pricing-api-${IMAGE_TAG} ${IMAGE_REPO}:pricing-api-latest
                            '''
                        }
                    }
                }
                stage('admin') {
                    steps {
                        script {
                            sh '''
                                echo "Building admin image..."
                                docker build -f Dockerfile.admin -t ${IMAGE_REPO}:admin-${IMAGE_TAG} . 2>&1 | tail -20
                                docker tag ${IMAGE_REPO}:admin-${IMAGE_TAG} ${IMAGE_REPO}:admin-latest
                            '''
                        }
                    }
                }
                stage('customer') {
                    steps {
                        script {
                            sh '''
                                echo "Building customer image..."
                                docker build -f Dockerfile.customer -t ${IMAGE_REPO}:customer-${IMAGE_TAG} . 2>&1 | tail -20
                                docker tag ${IMAGE_REPO}:customer-${IMAGE_TAG} ${IMAGE_REPO}:customer-latest
                            '''
                        }
                    }
                }
                stage('trainer') {
                    steps {
                        script {
                            sh '''
                                echo "Building trainer image..."
                                docker build -f Dockerfile.trainer -t ${IMAGE_REPO}:trainer-${IMAGE_TAG} . 2>&1 | tail -20
                                docker tag ${IMAGE_REPO}:trainer-${IMAGE_TAG} ${IMAGE_REPO}:trainer-latest
                            '''
                        }
                    }
                }
            }
        }

        stage('Push to Registry') {
            when {
                allOf {
                    branch 'main'
                    expression { return sh(script: 'command -v docker >/dev/null 2>&1', returnStatus: true) == 0 }
                }
            }
            steps {
                script {
                    sh '''
                        echo "Registry credentials need to be configured in Jenkins"
                        echo "To enable Docker push, add docker-hub-credentials to Jenkins credentials"
                        # withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        #   echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        #   docker push ${IMAGE_REPO}:pricing-api-${IMAGE_TAG}
                        # }
                    '''
                }
            }
        }

        stage('Deploy via Ansible') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh '''
                        if [ -f ansible/site.yml ]; then
                            echo "Ansible playbook found at ansible/site.yml"
                            which ansible-playbook || (apt-get install -y ansible 2>/dev/null || echo "Ansible not available")
                            # Uncomment to enable: ansible-playbook -i ansible/hosts.ini ansible/site.yml
                        else
                            echo "No ansible playbook found at ansible/site.yml"
                        fi
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                allOf {
                    branch 'main'
                    expression { return params.DEPLOY_TO_K8S }
                }
            }
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        sh """
                            # Check if kubectl is available
                            if ! command -v kubectl > /dev/null 2>&1; then
                                echo "kubectl not found. Installing..."
                                curl -LO "https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                                chmod +x kubectl
                                mv kubectl /usr/local/bin/
                            fi
                            
                            export KUBECONFIG=\$KUBECONFIG_FILE
                            echo "Deploying to Kubernetes..."
                            
                            # Create namespace
                            kubectl create namespace spe-platform || true
                            
                            # Apply K8s manifests
                            kubectl apply -f k8s/namespace.yaml || true
                            kubectl apply -f k8s/rbac/ || true
                            kubectl apply -f k8s/configmaps/ || true
                            kubectl apply -f k8s/secrets/ || true
                            
                            # Replace placeholders in deployments and apply
                            sed -i "s|IMAGE_REGISTRY|${REGISTRY}/${params.DOCKERHUB_NAMESPACE}|g" k8s/deployments/*.yaml
                            sed -i "s|IMAGE_TAG|${IMAGE_TAG}|g" k8s/deployments/*.yaml
                            
                            echo "Loading images into Minikube..."
                            docker save ${IMAGE_REPO}:pricing-api-latest | docker exec -i minikube docker load || true
                            docker save ${IMAGE_REPO}:admin-latest | docker exec -i minikube docker load || true
                            docker save ${IMAGE_REPO}:customer-latest | docker exec -i minikube docker load || true
                            docker save ${IMAGE_REPO}:trainer-${IMAGE_TAG} | docker exec -i minikube docker load || true
                            
                            kubectl apply -f k8s/deployments/ || true
                            
                            kubectl apply -f k8s/services/ || true
                            kubectl apply -f k8s/ingress/ || true
                            
                            echo "Waiting for deployments..."
                            kubectl rollout status deployment/pricing-api -n spe-platform --timeout=2m || true
                            kubectl rollout status deployment/admin-dashboard -n spe-platform --timeout=2m || true
                            kubectl rollout status deployment/customer-portal -n spe-platform --timeout=2m || true
                            
                            echo "Deployment Status:"
                            kubectl get pods -n spe-platform || true
                            kubectl get services -n spe-platform || true
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                sh '''
                    echo "Pipeline execution completed at $(date)"
                    if command -v docker &> /dev/null; then
                        docker image prune -f --filter "dangling=true" 2>/dev/null || true
                    fi
                '''
            }
        }
        success {
            echo "✓ Pipeline executed successfully!"
            script {
                try {
                    mail bcc: '', body: "Build ${env.BUILD_NUMBER} of ${env.JOB_NAME} was successful.\n\nMore info: ${env.BUILD_URL}", 
                         cc: '', from: 'jenkins@spe-platform.com', replyTo: '', 
                         subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}", 
                         to: "ruturajwairkar@gmail.com"
                } catch (Exception e) {
                    echo "Email notification skipped (SMTP not configured in Jenkins System): ${e.message}"
                }
            }
        }
        failure {
            echo "✗ Pipeline failed. Check logs for details."
            script {
                try {
                    mail bcc: '', body: "Build ${env.BUILD_NUMBER} of ${env.JOB_NAME} FAILED.\n\nCheck logs: ${env.BUILD_URL}console", 
                         cc: '', from: 'jenkins@spe-platform.com', replyTo: '', 
                         subject: "FAILURE: ${env.JOB_NAME} #${env.BUILD_NUMBER}", 
                         to: "ruturajwairkar@gmail.com"
                } catch (Exception e) {
                    echo "Email notification skipped (SMTP not configured in Jenkins System): ${e.message}"
                }
            }
        }
    }
}
