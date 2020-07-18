import {Injectable} from '@angular/core';
import {Account} from '../models/Account';
import {HttpClient} from '@angular/common/http';
import {AppConfig} from '../app.config';
import 'rxjs/add/operator/map';
import {Router} from "@angular/router";

@Injectable()
export class SignupService {

  constructor(private http: HttpClient, private config: AppConfig, private router: Router) {
    console.log("Signup constructor speaking!");
  }

  signUp(newAccount: Account) {
    return this.http.post(this.config.apiUrl + '/register',
      {email: newAccount.email, organizationName: newAccount.organizationName});
  }


}
