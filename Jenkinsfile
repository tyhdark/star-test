pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', credentialsId: '2432580e-3beb-42f7-ab8a-9859617d43f1', url: 'git@github.com:JW-Zhang001/star-test.git'
      }
    }

    stage('Build') {
      steps {
        sh 'echo "build"'
      }
    }

    stage('Deploy') {
      steps {
        sh 'ansible-playbook /home/xingdao/qa-home/roles/gea-chain/tests/test.yml -i /home/xingdao/qa-home/roles/gea-chain/tests/inventory --tags redeploy'
      }
//       post {
//         failure {
//           echo 'Deployment failed!'
//           currentBuild.result = 'FAILURE'
//         }
//       }
    }
  }
}