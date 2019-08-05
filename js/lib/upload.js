import Azure from 'azure-storage'

class AzureUploader {
  constructor(sasToken) {
    this.sasToken = sasToken.token
  }

  async upload(file, objectName) {
    const blobService = Azure.createBlobServiceWithSas(
      'https://atat.blob.core.windows.net',
      this.sasToken
    )
    const fileReader = new FileReader()
    const options = {
      contentSettings: {
        contentType: 'application/pdf',
      },
      metadata: {
        filename: file.name,
      },
    }

    return new Promise((resolve, reject) => {
      fileReader.addEventListener('load', function(f) {
        blobService.createBlockBlobFromText(
          'task-order-pdfs',
          `${objectName}.pdf`,
          f.target.result,
          options,
          function(err, result) {
            if (err) {
              reject(err)
            } else {
              resolve(result)
            }
          }
        )
      })
      fileReader.readAsText(file)
    })
  }
}

class AwsUploader {
  constructor(presignedPost) {
    this.presignedPost = presignedPost
  }

  async upload(file, objectName) {
    const form = new FormData()
    Object.entries(this.presignedPost.fields).forEach(([k, v]) => {
      form.append(k, v)
    })
    form.append('file', file)
    form.set('x-amz-meta-filename', file.name)

    return fetch(this.presignedPost.url, {
      method: 'POST',
      body: form,
    })
  }
}

class MockUploader {
  constructor(token) {
    this.token = token
  }

  async upload(file, objectName) {
    return Promise.resolve({})
  }
}

export const buildUploader = token => new MockUploader(token)
