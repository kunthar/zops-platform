import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {Router} from "@angular/router";
import {AppConfig} from "../app.config";

@Injectable()
export class GetUserInfoService {

  constructor(private http: HttpClient, private config: AppConfig, private router: Router) {
  }

  getUserInformation() {
    return this.http.get(this.config.apiUrl + "/me");
  }
}
