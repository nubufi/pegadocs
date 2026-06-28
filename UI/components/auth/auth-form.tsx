"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  ArrowRight,
  KeyRound,
  Mail,
} from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/input";
import { cn } from "@/lib/cn";
import { ApiError } from "@/lib/api/auth";
import { useAuthStore } from "@/stores/auth";

type AuthMode = "login" | "register";

const loginSchema = z.object({
  email: z.email("Enter a valid work email."),
  password: z.string().min(1, "Enter your password."),
});

const registerSchema = z.object({
  name: z.string().min(2, "Enter your full name."),
  email: z.email("Enter a valid work email."),
  password: z.string().min(8, "Use at least 8 characters."),
  company: z.string().min(2, "Enter your workspace or company."),
  phone: z.string().min(6, "Enter a phone number."),
  reference_code: z.string().optional(),
});

const forgotSchema = z.object({
  email: z.email("Enter a valid work email."),
});

const resetSchema = z.object({
  accessToken: z.string().min(1, "Paste the reset token from your email."),
  newPassword: z.string().min(8, "Use at least 8 characters."),
});

type LoginValues = z.infer<typeof loginSchema>;
type RegisterValues = z.infer<typeof registerSchema>;
type ForgotValues = z.infer<typeof forgotSchema>;
type ResetValues = z.infer<typeof resetSchema>;

function errorMessage(error: unknown) {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

function AuthTabs({ mode }: { mode: AuthMode }) {
  return (
    <div className="mb-7 grid grid-cols-2 rounded-[11px] border border-border bg-section p-1">
      <Link
        href="/login"
        className={cn(
          "rounded-lg px-3 py-2.5 text-center text-[13.5px] font-semibold transition-colors",
          mode === "login"
            ? "bg-white text-foreground shadow-[0_1px_3px_rgba(15,29,51,.1)]"
            : "text-muted-soft hover:text-foreground",
        )}
      >
        Sign in
      </Link>
      <Link
        href="/register"
        className={cn(
          "rounded-lg px-3 py-2.5 text-center text-[13.5px] font-semibold transition-colors",
          mode === "register"
            ? "bg-white text-foreground shadow-[0_1px_3px_rgba(15,29,51,.1)]"
            : "text-muted-soft hover:text-foreground",
        )}
      >
        Create account
      </Link>
    </div>
  );
}

function OAuthButtons({ verb }: { verb: "Continue" | "Sign up" }) {
  return (
    <div className="flex flex-col gap-2.5">
      <Button className="h-11 w-full bg-navy hover:bg-[#182944]" disabled>
        <span className="font-display text-sm font-bold">GH</span>
        {verb} with GitHub
      </Button>
      <Button variant="secondary" className="h-11 w-full text-foreground" disabled>
        <span className="font-display text-base font-bold text-[#4285f4]">G</span>
        {verb} with Google
      </Button>
    </div>
  );
}

function Divider() {
  return (
    <div className="my-[22px] flex items-center gap-3">
      <span className="h-px flex-1 bg-border" />
      <span className="font-mono text-[11px] text-muted-soft">OR</span>
      <span className="h-px flex-1 bg-border" />
    </div>
  );
}

function Notice({ type, children }: { type: "error" | "success"; children: string }) {
  return (
    <div
      className={cn(
        "mb-4 rounded-[10px] border px-3.5 py-3 text-sm leading-5",
        type === "error"
          ? "border-[#f0d3cf] bg-error-bg text-error"
          : "border-[#cbe9d8] bg-success-bg text-success",
      )}
    >
      {children}
    </div>
  );
}

export function LoginRegisterForm({ mode }: { mode: AuthMode }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);
  const registerUser = useAuthStore((state) => state.register);
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const isRegister = mode === "register";
  const nextPath = searchParams.get("next") || "/dashboard";

  const loginForm = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const registerForm = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      company: "",
      phone: "",
      reference_code: "",
    },
  });

  async function onLogin(values: LoginValues) {
    setFormError(null);
    setSuccess(null);
    try {
      await login(values);
      router.replace(nextPath);
    } catch (error) {
      setFormError(errorMessage(error));
    }
  }

  async function onRegister(values: RegisterValues) {
    setFormError(null);
    setSuccess(null);
    try {
      const message = await registerUser(values);
      setSuccess(message);
      registerForm.reset();
    } catch (error) {
      setFormError(errorMessage(error));
    }
  }

  return (
    <>
      <AuthTabs mode={mode} />
      <h2 className="font-display text-[26px] font-bold text-foreground">
        {isRegister ? "Create your account" : "Sign in to PegaDocs"}
      </h2>
      <p className="mb-6 mt-2 text-[14.5px] text-muted">
        {isRegister
          ? "Spin up a workspace and connect your first source."
          : "Welcome back. Pick up where you left off."}
      </p>

      <OAuthButtons verb={isRegister ? "Sign up" : "Continue"} />
      <Divider />

      {formError ? <Notice type="error">{formError}</Notice> : null}
      {success ? <Notice type="success">{success}</Notice> : null}

      {isRegister ? (
        <form
          className="flex flex-col gap-3.5"
          onSubmit={registerForm.handleSubmit(onRegister)}
        >
          <Field label="Full name" error={registerForm.formState.errors.name?.message}>
            <Input
              placeholder="Jane Doe"
              autoComplete="name"
              {...registerForm.register("name")}
            />
          </Field>
          <Field
            label="Work email"
            error={registerForm.formState.errors.email?.message}
          >
            <Input
              type="email"
              placeholder="you@company.com"
              autoComplete="email"
              {...registerForm.register("email")}
            />
          </Field>
          <Field
            label="Password"
            error={registerForm.formState.errors.password?.message}
          >
            <Input
              type="password"
              placeholder="At least 8 characters"
              autoComplete="new-password"
              {...registerForm.register("password")}
            />
          </Field>
          <div className="grid grid-cols-2 gap-3 max-[520px]:grid-cols-1">
            <Field
              label="Workspace"
              error={registerForm.formState.errors.company?.message}
            >
              <Input
                placeholder="acme-corp"
                autoComplete="organization"
                {...registerForm.register("company")}
              />
            </Field>
            <Field
              label="Phone"
              error={registerForm.formState.errors.phone?.message}
            >
              <Input
                placeholder="+1 555 0100"
                autoComplete="tel"
                {...registerForm.register("phone")}
              />
            </Field>
          </div>
          <Field
            label="Reference code"
            error={registerForm.formState.errors.reference_code?.message}
          >
            <Input
              placeholder="Optional"
              autoComplete="off"
              {...registerForm.register("reference_code")}
            />
          </Field>
          <Button
            type="submit"
            className="mt-1 h-[46px]"
            disabled={registerForm.formState.isSubmitting}
          >
            {registerForm.formState.isSubmitting ? "Creating..." : "Create account"}
            <ArrowRight size={17} />
          </Button>
        </form>
      ) : (
        <form
          className="flex flex-col gap-3.5"
          onSubmit={loginForm.handleSubmit(onLogin)}
        >
          <Field label="Work email" error={loginForm.formState.errors.email?.message}>
            <Input
              type="email"
              placeholder="you@company.com"
              autoComplete="email"
              {...loginForm.register("email")}
            />
          </Field>
          <Field
            label="Password"
            error={loginForm.formState.errors.password?.message}
          >
            <div className="mb-1 flex justify-end">
              <Link
                href="/forgot-password"
                className="text-[12.5px] font-semibold text-primary hover:text-primary-hover"
              >
                Forgot?
              </Link>
            </div>
            <Input
              type="password"
              placeholder="Your password"
              autoComplete="current-password"
              {...loginForm.register("password")}
            />
          </Field>
          <Button
            type="submit"
            className="mt-1 h-[46px]"
            disabled={loginForm.formState.isSubmitting}
          >
            {loginForm.formState.isSubmitting ? "Signing in..." : "Sign in"}
            <ArrowRight size={17} />
          </Button>
        </form>
      )}

      <p className="mt-5 text-center text-[13px] text-muted-soft">
        {isRegister
          ? "By creating an account you agree to the Terms & Privacy Policy."
          : "Self-hosted instance? Use your workspace SSO above."}
      </p>
    </>
  );
}

export function ForgotPasswordForm() {
  const forgotPassword = useAuthStore((state) => state.forgotPassword);
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const form = useForm<ForgotValues>({
    resolver: zodResolver(forgotSchema),
    defaultValues: { email: "" },
  });

  async function onSubmit(values: ForgotValues) {
    setFormError(null);
    setSuccess(null);
    try {
      const message = await forgotPassword(values.email);
      setSuccess(message);
    } catch (error) {
      setFormError(errorMessage(error));
    }
  }

  return (
    <>
      <h2 className="font-display text-[26px] font-bold text-foreground">
        Reset your password
      </h2>
      <p className="mb-6 mt-2 text-[14.5px] leading-6 text-muted">
        Enter your work email and PegaDocs will send the reset link.
      </p>
      {formError ? <Notice type="error">{formError}</Notice> : null}
      {success ? <Notice type="success">{success}</Notice> : null}
      <form className="flex flex-col gap-3.5" onSubmit={form.handleSubmit(onSubmit)}>
        <Field label="Work email" error={form.formState.errors.email?.message}>
          <Input
            type="email"
            placeholder="you@company.com"
            autoComplete="email"
            {...form.register("email")}
          />
        </Field>
        <Button type="submit" className="mt-1 h-[46px]" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Sending..." : "Send reset email"}
          <Mail size={17} />
        </Button>
      </form>
      <p className="mt-5 text-center text-[13px] text-muted-soft">
        <Link href="/login" className="font-semibold text-primary">
          Back to sign in
        </Link>
      </p>
    </>
  );
}

export function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const resetPassword = useAuthStore((state) => state.resetPassword);
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const defaultToken = useMemo(
    () => searchParams.get("access_token") ?? searchParams.get("token") ?? "",
    [searchParams],
  );
  const form = useForm<ResetValues>({
    resolver: zodResolver(resetSchema),
    values: { accessToken: defaultToken, newPassword: "" },
  });

  async function onSubmit(values: ResetValues) {
    setFormError(null);
    setSuccess(null);
    try {
      const message = await resetPassword(values.accessToken, values.newPassword);
      setSuccess(message);
      form.reset({ accessToken: values.accessToken, newPassword: "" });
    } catch (error) {
      setFormError(errorMessage(error));
    }
  }

  return (
    <>
      <h2 className="font-display text-[26px] font-bold text-foreground">
        Set a new password
      </h2>
      <p className="mb-6 mt-2 text-[14.5px] leading-6 text-muted">
        Use the reset token from your email and choose a new password.
      </p>
      {formError ? <Notice type="error">{formError}</Notice> : null}
      {success ? <Notice type="success">{success}</Notice> : null}
      <form className="flex flex-col gap-3.5" onSubmit={form.handleSubmit(onSubmit)}>
        <Field label="Reset token" error={form.formState.errors.accessToken?.message}>
          <Input
            placeholder="Paste token"
            autoComplete="one-time-code"
            {...form.register("accessToken")}
          />
        </Field>
        <Field
          label="New password"
          error={form.formState.errors.newPassword?.message}
        >
          <Input
            type="password"
            placeholder="At least 8 characters"
            autoComplete="new-password"
            {...form.register("newPassword")}
          />
        </Field>
        <Button type="submit" className="mt-1 h-[46px]" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Saving..." : "Update password"}
          <KeyRound size={17} />
        </Button>
      </form>
      <p className="mt-5 text-center text-[13px] text-muted-soft">
        <Link href="/login" className="font-semibold text-primary">
          Back to sign in
        </Link>
      </p>
    </>
  );
}
