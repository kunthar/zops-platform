import {NgModule} from '@angular/core';
import {RouterModule, PreloadAllModules, Routes} from '@angular/router';
import {AuthGuard} from './guards/auth.guard';
import {DashboardComponent} from './components/dashboard/dashboard.component';
import {SignupComponent} from './components/signup/signup.component';
import {SigninComponent} from './components/signin/signin.component';
import {HomeComponent} from './components/home/home.component';
import {DocsComponent} from './components/docs/docs.component';
import {HelpComponent} from './components/help/help.component';
import {ProductsComponent} from "./components/products/products.component";
import {ForgotPasswordComponent} from "./components/forgot-password/forgot-password.component";
import {PricingComponent} from "./components/pricing/pricing.component";
import {SolutionComponent} from "./components/solution/solution.component";
import {RocComponent} from "./components/products/roc/roc.component";
import {PushComponent} from "./components/products/push/push.component";
import {M2mComponent} from "./components/products/m2m/m2m.component";
import {SmsComponent} from "./components/products/sms/sms.component";
import {RocPricingComponent} from "./components/pricing/roc-pricing/roc-pricing.component";
import {PushPricingComponent} from "./components/pricing/push-pricing/push-pricing.component";
import {M2mPricingComponent} from "./components/pricing/m2m-pricing/m2m-pricing.component";
import {ApiComponent} from "./components/docs/api/api.component";
import {QuickstartComponent} from "./components/docs/quickstart/quickstart.component";
import {TutorialComponent} from "./components/docs/tutorial/tutorial.component";
import {GuideComponent} from "./components/docs/guide/guide.component";
import {BlogComponent} from "./components/docs/blog/blog.component";
import {NotfoundComponent} from "./components/notfound/notfound.component";
import {SignupApproveComponent} from "./components/signup-approve/signup-approve.component";
import {M2mHubComponent} from "./components/solution/m2m-hub/m2m-hub.component";
import {MarketingComponent} from "./components/solution/marketing/marketing.component";
import {RealtimeComponent} from "./components/solution/realtime/realtime.component";
import {LogoutComponent} from "./components/logout/logout.component";
import {ServiceComponent} from "./components/service/service.component";
import {AccountSettingsComponent} from "./components/account-settings/account-settings.component";
import {CookiePolicyComponent} from "./components/cookie-policy/cookie-policy.component";

const APP_ROUTES: Routes = [
  {path: '', component: HomeComponent},
  { // this part of route configuration will be use for all login needed pages with adding pages to children array.
    path: '',
    runGuardsAndResolvers: 'always',
    canActivateChild: [AuthGuard],
    children: [
      {
        path: 'dashboard',
        children: [
          {path: '', component: DashboardComponent},
          {path: ':projectId', component: DashboardComponent},
          {path: ':projectId/:serviceId', component: ServiceComponent}
        ]
      },
      {path: 'account-settings', component: AccountSettingsComponent}
    ]
  },
  {path: 'signin', component: SigninComponent},
  {path: 'logout', component: LogoutComponent},
  {path: 'signup', component: SignupComponent},
  {path: 'approve', component: SignupApproveComponent},
  {path: 'docs', component: DocsComponent},
  {path: 'forgot-password', component: ForgotPasswordComponent},
  {path: 'help', component: HelpComponent},
  {path: 'products', component: ProductsComponent},
  {path: 'roc', component: RocComponent},
  {path: 'push', component: PushComponent},
  {path: 'm2m', component: M2mComponent},
  {path: 'sms', component: SmsComponent},
  {path: 'pricing', component: PricingComponent},
  {path: 'roc-pricing', component: RocPricingComponent},
  {path: 'push-pricing', component: PushPricingComponent},
  {path: 'm2m-pricing', component: M2mPricingComponent},
  {path: 'api', component: ApiComponent},
  {path: 'quickstart', component: QuickstartComponent},
  {path: 'tutorial', component: TutorialComponent},
  {path: 'guide', component: GuideComponent},
  {path: 'blog', component: BlogComponent},
  {path: 'solution', component: SolutionComponent},
  {path: 'm2m-hub', component: M2mHubComponent},
  {path: 'marketing', component: MarketingComponent},
  {path: 'realtime', component: RealtimeComponent},
  {path: 'cookie-policy', component: CookiePolicyComponent},
  {path: '**', component: NotfoundComponent}
];

@NgModule({
  imports: [
    RouterModule.forRoot(APP_ROUTES, {preloadingStrategy: PreloadAllModules, enableTracing: true})
  ],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
