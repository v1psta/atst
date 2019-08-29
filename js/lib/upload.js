import Azure from 'azure-storage'
import 'whatwg-fetch'

class AzureUploader {
  constructor(accountName, containerName, sasToken, objectName) {
    this.accountName = accountName
    this.containerName = containerName
    this.sasToken = sasToken.token
    this.objectName = objectName
  }

  async upload(file) {
    const blobService = Azure.createBlobServiceWithSas(
      `https://${this.accountName}.blob.core.windows.net`,
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
      fileReader.addEventListener('load', f => {
        blobService.createBlockBlobFromText(
          this.containerName,
          `${this.objectName}`,
          f.target.result,
          options,
          (err, result) => {
            if (err) {
              resolve({ ok: false })
            } else {
              resolve({ ok: true, objectName: this.objectName })
            }
          }
        )
      })
      fileReader.readAsText(file)
    })
  }
}

class AwsUploader {
  constructor(presignedPost, objectName) {
    this.presignedPost = presignedPost
    this.objectName = objectName
  }

  async upload(file) {
    const form = new FormData()
    Object.entries(this.presignedPost.fields).forEach(([k, v]) => {
      form.append(k, v)
    })
    form.append('file', file)
    form.set('x-amz-meta-filename', file.name)

    const response = await fetch(this.presignedPost.url, {
      method: 'POST',
      body: form,
    })

    return { ok: response.ok, objectName: this.objectName }
  }
}

class MockUploader {
  constructor(token, objectName) {
    this.token = token
    this.objectName = objectName
  }

  async upload(file, objectName) {
    return Promise.resolve({ ok: true, objectName: this.objectName })
  }
}

export const buildUploader = (token, objectName) => {
  const cloudProvider = process.env.CLOUD_PROVIDER || 'mock'
  if (cloudProvider === 'aws') {
    return new AwsUploader(token, objectName)
  } else if (cloudProvider === 'azure') {
    return new AzureUploader(
      process.env.AZURE_ACCOUNT_NAME,
      process.env.AZURE_CONTAINER_NAME,
      token,
      objectName
    )
  } else {
    return new MockUploader(token, objectName)
  }
}
