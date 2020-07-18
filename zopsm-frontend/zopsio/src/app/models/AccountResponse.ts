export interface AccountResponse {
  meta: {
    params: {
      indent: number
    }
  },
  content: {
    organizationName: string,
    address: string,
    phone: number,
    email: string,
    registrationId: string
  }
}
