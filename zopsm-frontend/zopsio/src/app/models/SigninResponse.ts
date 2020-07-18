export interface SigninResponse {
  meta: {
    params: {
      indent: number;
    }
  },
  content: {
    token: string;
  }
}
