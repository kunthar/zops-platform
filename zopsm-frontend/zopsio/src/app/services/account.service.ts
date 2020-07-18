import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {AppConfig} from "../app.config";
import {Account} from "../models/Account";

@Injectable()
export class AccountService {

  constructor(private http: HttpClient, private config: AppConfig) {
  }

  getAccountData() {
    return this.http.get(this.config.apiUrl + "/account");
  }

  updateAccountData(updateAccount: Account) {
    return this.http.put(this.config.apiUrl + "/account", updateAccount);
  }

 /* deleteAccount() {
    return this.http.delete(this.config.apiUrl + "/account");
  } */
}
