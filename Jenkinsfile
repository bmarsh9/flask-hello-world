def group = "secops"
def service = "hello-flask"

pipeline {
  agent any
  stages {
    stage("Build Image") {
      steps {
        script {
          def customImage = docker.build("${group}_${service}")
        }
      }
    }
    stage("Scan Image") {
      steps {
        TwistlockScan(imageName:"${group}_${service}")
      }
    }
  }
}
