export interface UserInfo {
  meta: {
    params: {
      indent: number;
    }
  },
  content: {
    email: string,
    role: string,
    id: string,
    firstName: string,
    lastName: string
  }
}
