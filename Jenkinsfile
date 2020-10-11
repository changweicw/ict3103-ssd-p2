pipeline {
    agent none
    stages{
        stage('Build'){
            agent{
                docker{
                    image 'python:3.8'
                }
            }
            steps {
                sh 'python main.py'
            }
            stash(name: 'compiled-results', includes: 'sources/*.py*')
        }
    }

}