import {Component, Input, OnInit} from '@angular/core';
import {UserInfo} from "../../models/UserInfo";
import {GetUserInfoService} from "../../services/get-user-info.service";

@ Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {

  isUserLoggedIn = false;
  username: string;

  constructor(private getUserInfo: GetUserInfoService) {
    this.isUserLoggedIn = !!sessionStorage.getItem('currentUserToken');
    if(this.isUserLoggedIn){
      this.username = localStorage.getItem('username');
    }
  }

  ngOnInit() {
    if (this.isUserLoggedIn && !this.username) {
      this.getUserInfo.getUserInformation().subscribe(
        (res: UserInfo) => {
          this.username = res.content.firstName;
          localStorage.setItem('username', this.username);
        },
        error => {
          console.log(error)
        }
      );
    }
  }

}
