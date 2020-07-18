import {Injectable} from "@angular/core";
import {AppConfig} from "../app.config";
import "rxjs/add/operator/map";
import {HttpClient} from "@angular/common/http";
import {Router} from "@angular/router";

@Injectable()
export class SigninService {

  constructor(private http: HttpClient, private config: AppConfig, private router: Router) {
  }

  sendSigninRequest(email: string, password: string) {
    return this.http.post(this.config.apiUrl + "/session", {email: email, password: password});
  }

  sendLogoutRequest() {
    return this.http.options(this.config.apiUrl + "/session/logout")
      .subscribe(
        res => {
          sessionStorage.clear();
          localStorage.clear();
          // todo: set token as expired.
          this.router.navigate(["/"])
            .catch(error => {
              location.reload();
              console.log(error);
            });
        },
        error => {
          console.log(error);
        });
  }

  checkAuth() {
    if (sessionStorage.getItem("currentUserToken")) {
      return true;
    }
    this.router.navigate(["/signin"])
      .catch(error => {
        location.reload();
        console.log(error);
      });
    return false;
  }

}
