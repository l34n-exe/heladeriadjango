import { ref } from "vue";

export type SnackbarColor = "success" | "error" | "warning" | "info";

export function useFormFeedback() {
  const snackbar = ref(false);
  const snackbarColor = ref<SnackbarColor>("success");
  const snackbarText = ref("");

  const showFeedback = (message: string, color: SnackbarColor = "success") => {
    snackbarText.value = message;
    snackbarColor.value = color;
    snackbar.value = true;
  };

  const validateForm = async (
    formRef: { validate?: () => Promise<boolean | { valid: boolean }> } | null,
  ) => {
    const result = await formRef?.validate?.();

    if (result === undefined || result === false) {
      return false;
    }

    if (
      typeof result === "object" &&
      "valid" in result &&
      result.valid === false
    ) {
      return false;
    }

    return true;
  };

  return {
    snackbar,
    snackbarColor,
    snackbarText,
    showFeedback,
    validateForm,
  };
}
