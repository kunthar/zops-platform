export interface APIResponse {
  meta: {
    params: {
      indent: number
    }
  },
  content: {
    fcmApiKeys: string,
    fcmProjectNumber: string,
    apnsCert: string,
    id: string
  }
}
