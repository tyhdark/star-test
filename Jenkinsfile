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


    stage('Check Directory Permissions') {
        steps {
            sh 'sudo ls -l /home/xingdao/qa-home/roles'
        }
    }

    stage('Deploy') {
      steps {
        sh 'sudo cd /home/xingdao/qa-home && ansible-playbook roles/gea-chain/tests/test.yml -i roles/gea-chain/tests/inventory --tags redeploy --become --become-user=root'
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