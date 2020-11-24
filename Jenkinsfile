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
    stage("Twistlock") {
      steps {
        def scanResult = TwistlockScan(imageName:"${group}_${service}")
        GithubComment(comment:"test")
      }
    }
  }
}
