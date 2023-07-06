pipeline {
  agent any
  stages {
//     stage('Checkout') {
//       steps {
//         git branch: 'main', credentialsId: '2432580e-3beb-42f7-ab8a-9859617d43f1', url: 'git@github.com:JW-Zhang001/star-test.git'
//       }
//     }

    stage('Build') {
      steps {
        sh 'echo "build"'
      }
    }

    stage('Deploy') {
      steps {
          script {
            if (params.ENVIRONMENT == 'development') {
              sh 'cd /home/xingdao/qa-home && ansible-playbook roles/gea-chain/tests/test.yml -i roles/gea-chain/tests/develop/inventory --tags "$ansible_tags"'
            } else if (params.ENVIRONMENT == 'alpha-test') {
              sh 'cd /home/xingdao/qa-home && ansible-playbook roles/gea-chain/tests/test.yml -i roles/gea-chain/tests/alpha/inventory --tags "$ansible_tags"'
            } else if (params.ENVIRONMENT == 'beta-test') {
              sh 'cd /home/xingdao/qa-home && ansible-playbook roles/gea-chain/tests/test.yml -i roles/gea-chain/tests/beta/inventory --tags "$ansible_tags"'
            } else {
              error('Invalid environment specified!')
            }
          }
      }
      post {
        failure {
          echo 'Deployment failed!'
        }
      }
    }
  }
}