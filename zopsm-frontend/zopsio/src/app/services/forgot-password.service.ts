import {Injectable} from '@angular/core';
import {AppConfig} from "../app.config";
import {HttpClient} from "@angular/common/http";
import {Router} from "@angular/router";

@Injectable()
export class ForgotPasswordService {

  constructor(private http: HttpClient, private config: AppConfig, private router: Router) {

  }

  forgotPassword(email: string) {
    return this.http.post(this.config.apiUrl + '/forgot-password', {email: email});
  }

  resetPassword(password: string, token: string) {
    return this.http.put(this.config.apiUrl + '/reset-password', {password: password, resetToken: token});
  }
}
