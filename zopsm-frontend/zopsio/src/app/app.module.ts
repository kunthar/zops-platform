import {BrowserModule} from "@angular/platform-browser";
import {NgModule} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {HttpClientModule, HTTP_INTERCEPTORS} from "@angular/common/http";

import {AppComponent} from "./app.component";
import {HeaderComponent} from "./components/header/header.component";
import {FooterComponent} from "./components/footer/footer.component";
import {SigninComponent} from "./components/signin/signin.component";
import {DashboardComponent} from "./components/dashboard/dashboard.component";
import {SignupComponent} from "./components/signup/signup.component";

import {AuthGuard} from './guards/auth.guard';
import {AppConfig} from './app.config';
import {SigninService} from './services/signin.service';
import {SignupService} from './services/signup.service';
import {HomeComponent} from './components/home/home.component';
import {AppRoutingModule} from './app.routing';
import {DocsComponent} from './components/docs/docs.component';
import {HelpComponent} from './components/help/help.component';
import {ProductsComponent} from './components/products/products.component';
import {NoopInterceptor} from './services/NoopInterceptor';
import {ForgotPasswordComponent} from './components/forgot-password/forgot-password.component';
import {PricingComponent} from './components/pricing/pricing.component';
import {PushComponent} from './components/products/push/push.component';
import {M2mComponent} from './components/products/m2m/m2m.component';
import {SmsComponent} from './components/products/sms/sms.component';
import {RocComponent} from "./components/products/roc/roc.component";
import {RocPricingComponent} from "./components/pricing/roc-pricing/roc-pricing.component";
import {PushPricingComponent} from "./components/pricing/push-pricing/push-pricing.component";
import {M2mPricingComponent} from "./components/pricing/m2m-pricing/m2m-pricing.component";
import {ApiComponent} from "./components/docs/api/api.component";
import {QuickstartComponent} from "./components/docs/quickstart/quickstart.component";
import {TutorialComponent} from "./components/docs/tutorial/tutorial.component";
import {GuideComponent} from "./components/docs/guide/guide.component";
import {BlogComponent} from "./components/docs/blog/blog.component";
import {ShortFooterComponent} from "./components/footer/short-footer/short-footer.component";
import {HeaderDocsComponent} from "./components/header-docs/header-docs.component";
import {NotfoundComponent} from "./components/notfound/notfound.component";
import {SignupApproveComponent} from "./components/signup-approve/signup-approve.component";
import {ShowErrorsComponent} from "./components/show-errors/show-errors.component";
import {SignupApproveService} from "./services/signup-approve.service";
import {ForgotPasswordService} from "./services/forgot-password.service";
import {AnyErrorTemplate} from "./templates/any-error";
import {RECAPTCHA_SETTINGS, RecaptchaModule, RecaptchaSettings} from "ng-recaptcha";
import {RecaptchaFormsModule} from "ng-recaptcha/forms";
import {SolutionComponent} from './components/solution/solution.component';
import {M2mHubComponent} from './components/solution/m2m-hub/m2m-hub.component';
import {MarketingComponent} from './components/solution/marketing/marketing.component';
import {RealtimeComponent} from './components/solution/realtime/realtime.component';
import {HeaderDashboardComponent} from './components/header-dashboard/header-dashboard.component';
import {GetUserInfoService} from "./services/get-user-info.service";
import {ProjectService} from "./services/project.service";
import {ServiceService} from "./services/service.service";
import {LogoutComponent} from './components/logout/logout.component';
import {ServiceComponent} from './components/service/service.component';
import {AccountSettingsComponent} from './components/account-settings/account-settings.component';
import {AccountService} from "./services/account.service";
import {ApiService} from "./services/api.service";
import { CookiePolicyComponent } from './components/cookie-policy/cookie-policy.component';

const globalSettings: RecaptchaSettings = {siteKey: '6Lf-zD8UAAAAAJeS7mF9yTpllrGCiAqBGZoaPpxC'};

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    FooterComponent,
    SigninComponent,
    DashboardComponent,
    SignupComponent,
    HomeComponent,
    DocsComponent,
    HelpComponent,
    ProductsComponent,
    ForgotPasswordComponent,
    PricingComponent,
    PushComponent,
    M2mComponent,
    SmsComponent,
    RocComponent,
    RocPricingComponent,
    PushPricingComponent,
    M2mPricingComponent,
    ApiComponent,
    QuickstartComponent,
    TutorialComponent,
    GuideComponent,
    BlogComponent,
    ShortFooterComponent,
    HeaderDocsComponent,
    NotfoundComponent,
    SignupApproveComponent,
    ShowErrorsComponent,
    AnyErrorTemplate,
    SolutionComponent,
    M2mHubComponent,
    MarketingComponent,
    RealtimeComponent,
    HeaderDashboardComponent,
    LogoutComponent,
    ServiceComponent,
    AccountSettingsComponent,
    CookiePolicyComponent
  ],
  imports: [
    AppRoutingModule,
    BrowserModule,
    HttpClientModule,
    FormsModule,
    RecaptchaModule.forRoot(),
    RecaptchaFormsModule
  ],
  providers: [
    SigninService,
    SignupService,
    SignupApproveService,
    ForgotPasswordService,
    GetUserInfoService,
    ProjectService,
    ServiceService,
    AccountService,
    ApiService,
    AuthGuard,
    AppConfig,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: NoopInterceptor,
      multi: true,
    },
    {
      provide: RECAPTCHA_SETTINGS,
      useValue: globalSettings,
    },
  ],
  bootstrap: [AppComponent]
})

export class AppModule {
}
