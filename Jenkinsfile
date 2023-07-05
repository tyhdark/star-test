pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        // 检出 Python 项目的代码库
        git url: 'git@github.com:JW-Zhang001/star-test.git'
      }
    }

    stage('Build') {
      steps {
        echo 'build'
      }
    }

    stage('Deploy') {
      steps {
        // 运行 Ansible playbook 部署应用程序
        sh 'ansible-playbook /home/xingdao/qa-home/roles/gea-chain/tests/test.yml -i /home/xingdao/qa-home/roles/gea-chain/tests/inventory --tags redeploy'
      }

      post {
        // 如果部署失败，则将构建标记为失败
        failure {
          echo 'Deployment failed!'
          currentBuild.result = 'FAILURE'
        }
      }
    }
  }
}