{{/*
Expand the name of the chart.
*/}}
{{- define "codeplex-ai.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this
(by the DNS naming spec).
*/}}
{{- define "codeplex-ai.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "codeplex-ai.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels — applied to every resource we render.
*/}}
{{- define "codeplex-ai.labels" -}}
helm.sh/chart: {{ include "codeplex-ai.chart" . }}
{{ include "codeplex-ai.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: codeplex-ai
{{- end }}

{{/*
Selector labels — must be stable across releases, so do NOT include version
or chart labels here. Only what's safe to put in a Deployment selector.
*/}}
{{- define "codeplex-ai.selectorLabels" -}}
app.kubernetes.io/name: {{ include "codeplex-ai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Redis labels (component-scoped variant).
*/}}
{{- define "codeplex-ai.redis.labels" -}}
helm.sh/chart: {{ include "codeplex-ai.chart" . }}
app.kubernetes.io/name: {{ include "codeplex-ai.name" . }}-redis
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: redis
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: codeplex-ai
{{- end }}

{{- define "codeplex-ai.redis.selectorLabels" -}}
app.kubernetes.io/name: {{ include "codeplex-ai.name" . }}-redis
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "codeplex-ai.redis.fullname" -}}
{{- printf "%s-redis" (include "codeplex-ai.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
ServiceAccount name to use.
*/}}
{{- define "codeplex-ai.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "codeplex-ai.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Resolved Redis URL — uses the bundled Redis service when redis.enabled, else
falls back to whatever's in .Values.config.REDIS_URL (or empty).
*/}}
{{- define "codeplex-ai.redisUrl" -}}
{{- if .Values.redis.enabled }}
{{- printf "redis://%s:%d/0" (include "codeplex-ai.redis.fullname" .) (int .Values.redis.service.port) }}
{{- else }}
{{- default "" .Values.config.REDIS_URL }}
{{- end }}
{{- end }}

{{/*
Image reference — uses .image.tag, falling back to .Chart.AppVersion.
*/}}
{{- define "codeplex-ai.image" -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion -}}
{{- printf "%s:%s" .Values.image.repository $tag }}
{{- end }}
