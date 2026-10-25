// Serial synthetic browser checks against the existing guarded preview only.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const lab = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(lab, '../..');
const runtime = path.join(lab, 'runtime');
const recovery = path.join(root, '.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium} = await import(pathToFileURL(path.join(recovery,
  'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const origin = 'http://127.0.0.1:55446';
const browser = await chromium.launch({headless: true, args: [
  '--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run',
]});
const checks = {}, geometry = [], errors = [];
let context, page, session, outside = 0, failure, successfulSyntheticChanges = 0;
const contexts = [];

const startContext = async () => {
  context = await browser.newContext({serviceWorkers: 'block', reducedMotion: 'reduce',
    viewport: {width: 1366, height: 900}, hasTouch: true,
    extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}});
  contexts.push(context);
  await context.route('**/*', route => {
    if (new URL(route.request().url()).origin === origin) return route.continue();
    outside++; return route.abort();
  });
  await context.addInitScript(() => {
    localStorage.setItem('priceyard_onboarding_seen', '1');
    localStorage.setItem('priceyard_data_saver', '1');
    localStorage.setItem('priceyard_easy_reading', '1');
    localStorage.setItem('priceyard_dark_mode', '0');
  });
  page = await context.newPage();
  page.setDefaultTimeout(10000); page.setDefaultNavigationTimeout(12000);
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(origin + '/__test__/status');
  assert.equal((await page.evaluate(() => fetch('/__test__/status').then(r => r.json()))).synthetic_only, true);
};

const login = async email => {
  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill(email);
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  const response = page.waitForResponse(r => r.url() === origin + '/api/auth/browser/login'
    && r.request().method() === 'POST');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  const authenticated = await response;
  assert.equal(authenticated.status(), 200);
  session = await authenticated.json();
  assert.ok(session.csrf_token && session.session_id);
  await page.waitForURL('**/dashboard');
  return (await request('GET', '/auth/me')).data;
};

const request = async (method, endpoint, body) => page.evaluate(async ({method, endpoint, body, session}) => {
  const response = await fetch('/api' + endpoint, {method, credentials: 'same-origin',
    headers: {'Content-Type': 'application/json',
      ...(session ? {'X-PriceYard-Csrf': session.csrf_token, 'X-PriceYard-Session': session.session_id} : {})},
    ...(body === undefined ? {} : {body: JSON.stringify(body)})});
  let data = null;
  try { data = await response.json(); } catch { /* A body is not required for every response. */ }
  return {status: response.status, data};
}, {method, endpoint, body, session});

const visibleList = () => page.viewportSize().width <= 640
  ? page.locator('.admin-mobile-list') : page.locator('.admin-table-view');
const userRow = email => visibleList().locator(page.viewportSize().width <= 640 ? 'article.card' : 'tbody tr')
  .filter({hasText: email});
const role = email => userRow(email).locator('select');
const status = email => userRow(email).getByRole('button', {name: /^(?:Deactivate|Activate)$/, exact: true});
const openUsers = async () => {
  await page.goto(origin + '/admin/users');
  await page.getByRole('heading', {name: 'Users', exact: true}).waitFor();
  await userRow('owner@example.com').waitFor();
};
const changeRole = async (user, value) => {
  const response = page.waitForResponse(r => r.url() === `${origin}/api/users/${user.id}`
    && r.request().method() === 'PATCH');
  await role(user.email).selectOption(value);
  const changed = await response;
  assert.equal(changed.status(), 200);
  assert.equal((await changed.json()).role, value);
  successfulSyntheticChanges++;
  await page.waitForFunction(({email, value}) => [...document.querySelectorAll('.admin-table-view tbody tr')]
    .find(row => row.textContent.includes(email))?.querySelector('select')?.value === value, {email: user.email, value});
  await role(user.email).waitFor();
};
const changeStatus = async (user, active) => {
  const response = page.waitForResponse(r => r.url() === `${origin}/api/users/${user.id}`
    && r.request().method() === 'PATCH');
  await status(user.email).click();
  const changed = await response;
  assert.equal(changed.status(), 200);
  assert.equal((await changed.json()).is_active, active);
  successfulSyntheticChanges++;
  await userRow(user.email).getByRole('button', {name: active ? 'Deactivate' : 'Activate', exact: true}).waitFor();
};
const inspectOwnerProtection = async (email, width) => {
  await page.setViewportSize({width, height: width <= 640 ? 812 : 900});
  const row = userRow(email);
  await row.waitFor();
  assert.equal(await row.getAttribute('data-owner'), 'true');
  assert.equal(await row.locator('.owner-account-badge').innerText(), 'Owner');
  assert.equal(await role(email).isDisabled(), true);
  assert.equal(await status(email).isDisabled(), true);
  assert.match(await row.locator('.owner-account-note').innerText(), /Protected Owner account/);
  await row.evaluate(node => {
    const header = document.querySelector('.site-header').getBoundingClientRect();
    scrollTo(0, Math.max(0, scrollY + node.getBoundingClientRect().top - header.height - 12));
  });
  const shape = await row.evaluate(node => ({left: node.getBoundingClientRect().left,
    right: node.getBoundingClientRect().right, overflow: document.documentElement.scrollWidth > innerWidth + 1}));
  assert.equal(shape.overflow, false);
  geometry.push({control: 'Owner row', viewportWidth: width, ...shape});
  await page.screenshot({path: path.join(runtime, `owner-protection-users-${width}.png`), fullPage: false});
};

try {
  await startContext();
  const owner = await login('owner@example.com');
  assert.equal(owner.role, 'admin'); assert.equal(owner.is_owner, true);
  const originalPrices = (await request('GET', '/price-updates')).data;
  const ownerSubscription = await request('GET', `/subscriptions/${owner.id}`);
  assert.equal(ownerSubscription.status, 200); assert.equal(ownerSubscription.data.status, 'expired');
  await page.locator('.access-strip').getByText('Owner', {exact: true}).waitFor();
  await page.goto(origin + '/history'); await page.locator('.history-filters').waitFor();
  checks.owner_keeps_full_access_with_an_expired_subscription_using_real_cookie_login = true;

  await page.goto(origin + '/admin');
  await page.locator('.admin-metric').nth(13).waitFor();
  assert.equal(await page.locator('.admin-metric').count(), 14);
  checks.owner_retains_all_fourteen_original_admin_dashboard_cards = true;

  await openUsers();
  const users = await request('GET', '/users/page');
  assert.equal(users.status, 200);
  const target = users.data.items.find(user => user.email === 'free@example.com');
  const ordinaryAdmin = users.data.items.find(user => user.email === 'admin@example.com');
  assert.ok(target && ordinaryAdmin); assert.equal(ordinaryAdmin.is_owner, false);
  const userIds = users.data.items.map(user => user.id).sort((a, b) => a - b);
  await inspectOwnerProtection(owner.email, 1366);
  await inspectOwnerProtection(owner.email, 375);
  checks.owner_account_is_visibly_protected_in_desktop_and_mobile_controls = true;

  await page.setViewportSize({width: 1366, height: 900});
  assert.equal(await role(ordinaryAdmin.email).isEnabled(), true);
  assert.equal(await status(ordinaryAdmin.email).isEnabled(), true);
  await changeRole(target, 'admin');
  await changeRole(target, 'reporter');
  await changeRole(target, 'free_user');
  checks.owner_can_appoint_and_remove_admins_and_manage_non_admin_roles_through_existing_ui = true;

  await page.goto(origin + '/admin/subscriptions');
  const ownerSubRow = page.locator('.admin-table tbody tr[data-owner="true"]');
  await ownerSubRow.waitFor();
  assert.equal(await ownerSubRow.locator('select').inputValue(), 'expired');
  assert.match(await ownerSubRow.locator('.owner-account-note').innerText(), /Owner access does not expire/);
  assert.deepEqual((await request('GET', `/subscriptions/${owner.id}`)).data, ownerSubscription.data);
  checks.owner_subscription_history_is_preserved_and_explained_without_a_fake_renewal = true;
  await context.close();

  await startContext();
  const admin = await login('admin@example.com');
  assert.equal(admin.role, 'admin'); assert.equal(admin.is_owner, false);
  await page.locator('.access-strip').getByText('Admin', {exact: true}).waitFor();
  await page.goto(origin + '/admin'); await page.locator('.admin-metric').nth(13).waitFor();
  assert.equal(await page.locator('.admin-metric').count(), 14);
  await openUsers();
  for (const width of [1366, 375]) {
    await page.setViewportSize({width, height: width <= 640 ? 812 : 900});
    assert.equal(await role(owner.email).isDisabled(), true);
    assert.equal(await status(owner.email).isDisabled(), true);
    assert.equal(await role(admin.email).isDisabled(), true);
    assert.equal(await status(admin.email).isDisabled(), true);
    assert.equal(await role(target.email).isEnabled(), true);
    assert.equal(await status(target.email).isEnabled(), true);
    assert.equal(await role(target.email).locator('option[value="admin"]').count(), 0);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
  }
  checks.other_admin_retains_dashboard_but_cannot_edit_owner_or_admins_in_either_layout = true;

  await page.setViewportSize({width: 1366, height: 900});
  await changeRole(target, 'reporter'); await changeRole(target, 'free_user');
  await changeStatus(target, false); await changeStatus(target, true);
  checks.other_admin_can_still_manage_normal_non_admin_roles_and_active_status = true;

  const beforeDenied = (await request('GET', `/users/${owner.id}`)).data;
  for (const [id, payload] of [[owner.id, {is_active: false}], [admin.id, {role: 'free_user'}], [target.id, {role: 'admin'}]]) {
    const denied = await request('PATCH', `/users/${id}`, payload);
    assert.equal(denied.status, 403);
  }
  assert.deepEqual((await request('GET', `/users/${owner.id}`)).data, beforeDenied);
  const finalUsers = (await request('GET', '/users/page')).data;
  assert.deepEqual(finalUsers.items.map(user => user.id).sort((a, b) => a - b), userIds);
  assert.equal(finalUsers.items.find(user => user.id === target.id).role, 'free_user');
  assert.equal(finalUsers.items.find(user => user.id === target.id).is_active, true);
  assert.deepEqual((await request('GET', '/price-updates')).data, originalPrices);
  assert.equal(await page.locator('.header-search-link').isVisible(), true);
  checks.actual_csrf_verified_api_denies_privilege_bypass_without_changing_owner_prices_or_user_records = true;
  assert.deepEqual(errors, []); assert.equal(outside, 0);
} catch (error) {
  failure = error.stack || String(error);
  if (page && !page.isClosed()) await page.screenshot({path: path.join(runtime, 'owner-protection-failure.png'), fullPage: false}).catch(() => {});
} finally {
  const report = {passed: Object.keys(checks).length, checks, geometry, failure,
    real_api_cookie_login: true, mocked_identity_responses: 0,
    external_page_requests: outside, page_errors: errors, synthetic_only: true,
    production_connections: 0, production_records_changed: 0,
    successful_synthetic_user_changes: successfulSyntheticChanges};
  fs.writeFileSync(path.join(runtime, 'owner-protection-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  for (const current of contexts) await current.close().catch(() => {});
  await browser.close();
  if (failure) process.exitCode = 1;
}
