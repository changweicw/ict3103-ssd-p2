pipeline {
    agent {
        docker {
            image 'python:3.8'
        }
    }
    stages {
        stage('build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

    }
}