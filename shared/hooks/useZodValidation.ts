// React Hook para Validação de Formulários com Zod
// Integração entre React Hook Form e Zod schemas

import { useForm, UseFormReturn, FieldValues } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ZodSchema, ZodError } from 'zod';
import { useState, useCallback } from 'react';

// ===== HOOK PRINCIPAL =====

interface UseZodFormOptions<T extends FieldValues> {
  schema: ZodSchema<T>;
  defaultValues?: Partial<T>;
  mode?: 'onChange' | 'onBlur' | 'onSubmit' | 'onTouched' | 'all';
}

interface UseZodFormReturn<T extends FieldValues> extends UseFormReturn<T> {
  isValidating: boolean;
  validationErrors: string[];
  validateField: (fieldName: keyof T, value: any) => Promise<boolean>;
  validateForm: () => Promise<boolean>;
  getFieldError: (fieldName: keyof T) => string | undefined;
  clearFieldError: (fieldName: keyof T) => void;
  setFormData: (data: Partial<T>) => void;
}

export function useZodForm<T extends FieldValues>({
  schema,
  defaultValues,
  mode = 'onChange'
}: UseZodFormOptions<T>): UseZodFormReturn<T> {
  const [isValidating, setIsValidating] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const form = useForm<T>({
    resolver: zodResolver(schema),
    defaultValues,
    mode,
    criteriaMode: 'all',
    shouldFocusError: true
  });

  // Validar campo individual
  const validateField = useCallback(async (fieldName: keyof T, value: any): Promise<boolean> => {
    setIsValidating(true);
    
    try {
      // Criar objeto temporário para validação
      const currentValues = form.getValues();
      const testData = { ...currentValues, [fieldName]: value };
      
      // Validar usando Zod
      schema.parse(testData);
      
      // Limpar erro do campo se válido
      form.clearErrors(fieldName as any);
      setIsValidating(false);
      return true;
      
    } catch (error) {
      if (error instanceof ZodError) {
        const fieldError = error.errors.find(err => 
          err.path.includes(fieldName as string)
        );
        
        if (fieldError) {
          form.setError(fieldName as any, {
            type: 'validation',
            message: fieldError.message
          });
        }
      }
      
      setIsValidating(false);
      return false;
    }
  }, [schema, form]);

  // Validar formulário completo
  const validateForm = useCallback(async (): Promise<boolean> => {
    setIsValidating(true);
    setValidationErrors([]);
    
    try {
      const currentValues = form.getValues();
      schema.parse(currentValues);
      
      setIsValidating(false);
      return true;
      
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map(err => err.message);
        setValidationErrors(errors);
        
        // Definir erros nos campos
        error.errors.forEach(err => {
          if (err.path.length > 0) {
            const fieldName = err.path[0] as keyof T;
            form.setError(fieldName as any, {
              type: 'validation',
              message: err.message
            });
          }
        });
      }
      
      setIsValidating(false);
      return false;
    }
  }, [schema, form]);

  // Obter erro de campo específico
  const getFieldError = useCallback((fieldName: keyof T): string | undefined => {
    const fieldState = form.getFieldState(fieldName as any);
    return fieldState.error?.message;
  }, [form]);

  // Limpar erro de campo específico
  const clearFieldError = useCallback((fieldName: keyof T): void => {
    form.clearErrors(fieldName as any);
  }, [form]);

  // Definir dados do formulário com validação
  const setFormData = useCallback((data: Partial<T>): void => {
    Object.entries(data).forEach(([key, value]) => {
      form.setValue(key as any, value, { 
        shouldValidate: mode !== 'onSubmit',
        shouldDirty: true 
      });
    });
  }, [form, mode]);

  return {
    ...form,
    isValidating,
    validationErrors,
    validateField,
    validateForm,
    getFieldError,
    clearFieldError,
    setFormData
  };
}

// ===== HOOK PARA VALIDAÇÃO ASSÍNCRONA =====

interface UseAsyncValidationOptions {
  debounceMs?: number;
  validateOnMount?: boolean;
}

export function useAsyncValidation<T extends FieldValues>(
  schema: ZodSchema<T>,
  options: UseAsyncValidationOptions = {}
) {
  const { debounceMs = 300, validateOnMount = false } = options;
  const [isValidating, setIsValidating] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isValid, setIsValid] = useState(!validateOnMount);

  // Debounce para evitar validações excessivas
  const debounceTimeout = useCallback((fn: Function, delay: number) => {
    let timeoutId: NodeJS.Timeout;
    return (...args: any[]) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn.apply(null, args), delay);
    };
  }, []);

  const validateData = useCallback(async (data: Partial<T>): Promise<boolean> => {
    setIsValidating(true);
    setErrors({});

    try {
      schema.parse(data);
      setIsValid(true);
      setIsValidating(false);
      return true;
      
    } catch (error) {
      if (error instanceof ZodError) {
        const fieldErrors: Record<string, string> = {};
        
        error.errors.forEach(err => {
          if (err.path.length > 0) {
            const fieldName = err.path.join('.');
            fieldErrors[fieldName] = err.message;
          }
        });
        
        setErrors(fieldErrors);
      }
      
      setIsValid(false);
      setIsValidating(false);
      return false;
    }
  }, [schema]);

  const debouncedValidate = debounceTimeout(validateData, debounceMs);

  return {
    isValidating,
    errors,
    isValid,
    validate: validateData,
    debouncedValidate
  };
}

// ===== HOOK PARA VALIDAÇÃO DE CAMPO ÚNICO =====

export function useFieldValidation<T>(
  fieldSchema: ZodSchema<T>,
  initialValue?: T
) {
  const [value, setValue] = useState<T | undefined>(initialValue);
  const [error, setError] = useState<string | undefined>();
  const [isValidating, setIsValidating] = useState(false);
  const [isValid, setIsValid] = useState(false);

  const validate = useCallback(async (newValue: T): Promise<boolean> => {
    setIsValidating(true);
    setError(undefined);

    try {
      fieldSchema.parse(newValue);
      setIsValid(true);
      setIsValidating(false);
      return true;
      
    } catch (error) {
      if (error instanceof ZodError) {
        setError(error.errors[0]?.message);
      }
      
      setIsValid(false);
      setIsValidating(false);
      return false;
    }
  }, [fieldSchema]);

  const updateValue = useCallback(async (newValue: T) => {
    setValue(newValue);
    await validate(newValue);
  }, [validate]);

  return {
    value,
    error,
    isValidating,
    isValid,
    setValue: updateValue,
    validate
  };
}

// ===== UTILITÁRIOS DE VALIDAÇÃO =====

export class ValidationUtils {
  
  // Validar dados com schema e retornar erros formatados
  static validateWithSchema<T>(schema: ZodSchema<T>, data: unknown): {
    success: boolean;
    data?: T;
    errors?: Array<{ field: string; message: string }>;
  } {
    try {
      const validData = schema.parse(data);
      return { success: true, data: validData };
      
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message
        }));
        
        return { success: false, errors };
      }
      
      return { 
        success: false, 
        errors: [{ field: 'unknown', message: 'Validation failed' }] 
      };
    }
  }

  // Validar parcialmente (útil para formulários em etapas)
  static validatePartial<T>(schema: ZodSchema<T>, data: unknown): {
    success: boolean;
    data?: Partial<T>;
    errors?: Array<{ field: string; message: string }>;
  } {
    try {
      const partialSchema = schema.partial();
      const validData = partialSchema.parse(data);
      return { success: true, data: validData };
      
    } catch (error) {
      if (error instanceof ZodError) {
        const errors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message
        }));
        
        return { success: false, errors };
      }
      
      return { 
        success: false, 
        errors: [{ field: 'unknown', message: 'Validation failed' }] 
      };
    }
  }

  // Sanitizar dados antes da validação
  static sanitizeData(data: Record<string, any>): Record<string, any> {
    const sanitized: Record<string, any> = {};
    
    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        if (typeof value === 'string') {
          sanitized[key] = value.trim();
        } else if (Array.isArray(value)) {
          sanitized[key] = value.filter(item => 
            item !== null && item !== undefined && item !== ''
          );
        } else {
          sanitized[key] = value;
        }
      }
    });
    
    return sanitized;
  }

  // Formatar erros para exibição em UI
  static formatErrorsForUI(errors: ZodError): Record<string, string[]> {
    const formatted: Record<string, string[]> = {};
    
    errors.errors.forEach(error => {
      const fieldPath = error.path.join('.');
      
      if (!formatted[fieldPath]) {
        formatted[fieldPath] = [];
      }
      
      formatted[fieldPath].push(error.message);
    });
    
    return formatted;
  }
}

// ===== COMPONENTE DE ERRO =====

interface ValidationErrorProps {
  error?: string;
  errors?: string[];
  className?: string;
}

export function ValidationError({ error, errors, className = '' }: ValidationErrorProps) {
  const errorList = errors || (error ? [error] : []);
  
  if (errorList.length === 0) return null;
  
  return (
    <div className={`validation-error text-red-600 text-sm mt-1 ${className}`}>
      {errorList.length === 1 ? (
        <p>{errorList[0]}</p>
      ) : (
        <ul className="list-disc list-inside">
          {errorList.map((err, index) => (
            <li key={index}>{err}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ===== HOOK PARA FORMULÁRIOS COM ETAPAS =====

export function useMultiStepForm<T extends FieldValues>(
  schema: ZodSchema<T>,
  steps: Array<(keyof T)[]>
) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  
  const form = useZodForm({ schema });

  const validateCurrentStep = useCallback(async (): Promise<boolean> => {
    const currentStepFields = steps[currentStep];
    const currentStepData = currentStepFields.reduce((acc, field) => {
      acc[field] = form.getValues(field as any);
      return acc;
    }, {} as Partial<T>);

    try {
      // Criar schema parcial apenas para os campos da etapa atual
      const stepSchema = schema.pick(
        currentStepFields.reduce((acc, field) => {
          acc[field] = true;
          return acc;
        }, {} as Record<keyof T, true>)
      );

      stepSchema.parse(currentStepData);
      
      setCompletedSteps(prev => new Set([...prev, currentStep]));
      return true;
      
    } catch (error) {
      if (error instanceof ZodError) {
        error.errors.forEach(err => {
          if (err.path.length > 0) {
            const fieldName = err.path[0] as keyof T;
            form.setError(fieldName as any, {
              type: 'validation',
              message: err.message
            });
          }
        });
      }
      
      setCompletedSteps(prev => {
        const newSet = new Set([...prev]);
        newSet.delete(currentStep);
        return newSet;
      });
      
      return false;
    }
  }, [currentStep, steps, schema, form]);

  const nextStep = useCallback(async (): Promise<boolean> => {
    const isValid = await validateCurrentStep();
    
    if (isValid && currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
      return true;
    }
    
    return false;
  }, [currentStep, steps.length, validateCurrentStep]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const goToStep = useCallback((stepIndex: number) => {
    if (stepIndex >= 0 && stepIndex < steps.length) {
      setCurrentStep(stepIndex);
    }
  }, [steps.length]);

  return {
    ...form,
    currentStep,
    totalSteps: steps.length,
    completedSteps: Array.from(completedSteps),
    isStepCompleted: (stepIndex: number) => completedSteps.has(stepIndex),
    canGoToStep: (stepIndex: number) => stepIndex <= currentStep || completedSteps.has(stepIndex),
    nextStep,
    prevStep,
    goToStep,
    validateCurrentStep,
    isFirstStep: currentStep === 0,
    isLastStep: currentStep === steps.length - 1,
    currentStepFields: steps[currentStep]
  };
}
