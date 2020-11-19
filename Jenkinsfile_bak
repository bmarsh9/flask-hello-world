def group = "secops"
def service = "hello-flask"

pipeline {
  //checkout scm
  //agent { dockerfile true }
  agent any
  stages {
    stage("Build Image") {
      steps {
        script {
          def customImage = docker.build("${group}_${service}")
        }
      }
    }
    stage('Scan') {
        steps {
            // Scan the image
            prismaCloudScanImage ca: '',
            cert: '',
            dockerAddress: 'unix:///var/run/docker.sock',
            image: "${group}_${service}",
            key: '',
            logLevel: 'debug',
            podmanPath: '',
            project: '',
            resultsFile: 'prisma-cloud-scan-results.json',
            ignoreImageBuildTime:true
        }
    }
    stage('Generate Report') {
      steps {
        sh '/usr/bin/python3 /home/bmarsh/test.py --file prisma-cloud-scan-results.json --template /home/bmarsh/reports/templates/standard.html --output '+pwd()+'/reports'
      }
      post {
        success {
          publishHTML([
            allowMissing: false,
            alwaysLinkToLastBuild: false,
            keepAll: false,
            reportDir: 'reports',
            reportFiles: 'standard.html',
            reportName: 'Twistlock Report',
          ])
          publishChecks detailsURL: 'https://google.com', name: 'test-check', summary: 'just checking out the feature', text: 'vulns: 18, critical: 10, high: 8', title: 'Test Check'
        }
      }
    }
  }
//  post {
//      always {
//          prismaCloudPublish resultsFilePattern: 'prisma-cloud-scan-results.json'
//      }
//  }
}
