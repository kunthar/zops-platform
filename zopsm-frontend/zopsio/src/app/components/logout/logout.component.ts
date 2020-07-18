import {Component} from '@angular/core';
import {SigninService} from "../../services/signin.service";

@Component({
  selector: module.id,
  template: "<div>{{globalLoader}}</div>"
})
export class LogoutComponent {

  constructor(private logout: SigninService) {
    this.logout.sendLogoutRequest();
  }

}
