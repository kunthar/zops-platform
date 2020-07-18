import {Component, OnInit} from "@angular/core";
import {AccountService} from "../../services/account.service";
import {Router} from "@angular/router";
import {AccountResponse} from "../../models/AccountResponse";
import {Account} from "../../models/Account";

@Component({
  selector: "app-account-settings",
  templateUrl: "./account-settings.component.html",
  styleUrls: ["./account-settings.component.css"]
})
export class AccountSettingsComponent implements OnInit {

  loading = false;
  anyError = false;
  data: any = {};
  accountModel = new Account();

  constructor(private router: Router, private accountService: AccountService) {
  }

  ngOnInit() {
    this.getAccount();
  }

  getAccount() {
    const t = this;
    t.accountService.getAccountData().subscribe(
      (res: AccountResponse) => {
        this.data = res.content;
      },
      error => {
        console.log(error);
      }
    );
  }

  updateAccount() {
    this.loading = true;
    this.accountService.updateAccountData(this.accountModel).subscribe(
      res => {
        location.reload();
      },
      error => {
        this.loading = false;
        this.anyError = true;
        console.log(error);
      });
  }

}
