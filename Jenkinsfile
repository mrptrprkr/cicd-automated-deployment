pipeline {
    agent any

    environment {
        IMAGE_NAME = 'cicd-ops-dashboard'
        CONTAINER_NAME = 'cicd-ops-dashboard'
        APP_PORT = '8080'
        APP_ENV = 'production'
        APP_VERSION = '1.0.1'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated tests...'

                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --quiet -r requirements-dev.txt
                    .venv/bin/pytest -v
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker image...'

                sh '''
                    docker build \
                      -t ${IMAGE_NAME}:${BUILD_NUMBER} \
                      .
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application with protected credentials...'

                withCredentials([
                    string(
                        credentialsId: 'dashboard-api-token',
                        variable: 'DASHBOARD_API_TOKEN'
                    )
                ]) {
                    sh '''
                        docker rm -f ${CONTAINER_NAME} 2>/dev/null || true

                        docker run -d \
                          --name ${CONTAINER_NAME} \
                          --restart unless-stopped \
                          --network cicd-network \
                          -p ${APP_PORT}:8080 \
                          -e APP_ENV=${APP_ENV} \
                          -e APP_VERSION=${APP_VERSION} \
                          -e BUILD_NUMBER=${BUILD_NUMBER} \
                          -e GIT_COMMIT=${GIT_COMMIT} \
                          -e DEPLOYED_BY=Jenkins \
                          -e DASHBOARD_API_TOKEN="${DASHBOARD_API_TOKEN}" \
                          ${IMAGE_NAME}:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Verify') {
            steps {
                echo 'Waiting for application health check...'

                sh '''
                    for i in $(seq 1 12); do
                        STATUS=$(docker inspect \
                          --format='{{.State.Health.Status}}' \
                          ${CONTAINER_NAME} 2>/dev/null || true)

                        echo "Health status: ${STATUS}"

                        if [ "${STATUS}" = "healthy" ]; then
                            exit 0
                        fi

                        sleep 5
                    done

                    echo "Application did not become healthy."
                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                echo 'Running authenticated post-deployment smoke tests...'

                withCredentials([
                    string(
                        credentialsId: 'dashboard-api-token',
                        variable: 'DASHBOARD_API_TOKEN'
                    )
                ]) {
                    sh '''
                        curl --fail --silent \
                          http://${CONTAINER_NAME}:8080/health
                        echo

                        curl --fail --silent \
                          http://${CONTAINER_NAME}:8080/api/status
                        echo

                        set +x
                        curl --fail --silent \
                          -H "X-API-Key: ${DASHBOARD_API_TOKEN}" \
                          http://${CONTAINER_NAME}:8080/api/secure
                        echo
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'CI/CD pipeline failed.'
        }

        always {
            echo "Build ${BUILD_NUMBER} finished."
        }
    }
}
