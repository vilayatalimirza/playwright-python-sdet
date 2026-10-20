pipeline {
    agent { label 'built-in' }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        IMAGE_TAG = "playwright-python-sdet:${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Building ${env.JOB_NAME} #${env.BUILD_NUMBER} from ${env.GIT_COMMIT}"
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t ${IMAGE_TAG} .'
            }
        }

        stage('Test') {
            steps {
                sh 'mkdir -p reports'
                // Create + start + copy out + clean up. No bind mount, so the
                // nested Windows/WSL path problem cannot occur. docker cp goes
                // through the Docker API, not the filesystem.
                sh '''
                    CID=$(docker create ${IMAGE_TAG} pytest -v --junitxml=reports/junit.xml)
                    TEST_EXIT=0
                    docker start -a "$CID" || TEST_EXIT=$?
                    docker cp "$CID:/app/reports/." ./reports/ || true
                    docker rm -f "$CID" || true
                    exit $TEST_EXIT
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rmi ${IMAGE_TAG} || true'
            archiveArtifacts artifacts: 'reports/**/*.xml', allowEmptyArchive: true
            echo 'Pipeline finished'
        }
        success {
            junit 'reports/*.xml'
        }
        failure {
            echo 'Pipeline FAILED - check the Test stage output above'
        }
    }
}