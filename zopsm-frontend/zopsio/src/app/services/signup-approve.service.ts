import {Injectable} from '@angular/core';
import {AccountApprove} from "../models/AccountApprove";
import {AppConfig} from "../app.config";
import {HttpClient} from "@angular/common/http";

@Injectable()
export class SignupApproveService {


  constructor(private http: HttpClient, private config: AppConfig) {
  }

  signUpApprove(model: AccountApprove) {
    const t = this;
    return t.http.put(t.config.apiUrl + '/register/' + model.registrationId,
      {
        approveCode: model.approveCode,
        firstName: model.firstName,
        lastName: model.lastName,
        email: model.email,
        password: model.password
      });
  }
}
