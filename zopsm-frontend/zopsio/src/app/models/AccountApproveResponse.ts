export interface AccountApproveResponse {
  meta: {
    params: {
      indent: number
    }
  },
  content: {
    id: string;
    token: string;
    email: string;
    firstName: string;
    lastName: string;
  }
}
