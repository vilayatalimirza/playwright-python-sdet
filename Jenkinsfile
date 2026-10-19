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
                sh 'mkdir -p reports && chmod 777 reports'
                sh 'docker run --rm -v "$PWD/reports:/app/reports" ${IMAGE_TAG} pytest -v --junitxml=reports/junit.xml'
            }
        }
    }

    post {
        always {
            sh 'docker rmi ${IMAGE_TAG} || true'
            archiveArtifacts artifacts: 'reports/**/*.html', allowEmptyArchive: true
        }
        success {
            junit 'reports/*.xml'
        }
        failure {
            echo 'Pipeline FAILED - check the Test stage output above'
        }
    }
}