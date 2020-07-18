import {Component} from '@angular/core';
import {SigninService} from "./services/signin.service";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {

  constructor(private user: SigninService){
    let token = sessionStorage.getItem("currentUserToken");
    if(token){ // todo: check token is expired or not.
      //this.user.sendLogoutRequest();
    }
  }
}
