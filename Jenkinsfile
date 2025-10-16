pipeline {
    agent {
        dockerfile {
            filename 'docker/Dockerfile.simulator'
            dir 'docker' 
        }
    }
    stages {
        stage('Build and Test') {
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt' 
                sh 'python -m pytest tests/' 
            }
        }
        stage('Run Simulation') {
            steps {
                sh './scripts/run_simulation.sh' 
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'logs/results.csv, graphs/*.png'
            junit 'test-reports/*.xml' 
        }
    }
}