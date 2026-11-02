import { Navigate, createBrowserRouter } from 'react-router-dom';
import { Login } from '../pages/auth/Login';
import { Dashboard } from '../pages/dashboard/Dashboard';
import { DashboardLayout } from '../components/layout/DashboardLayout';
import { ProtectedRoute, PublicRoute } from '../components/auth/ProtectedRoute';
import { SubjectsList } from '../pages/subjects/SubjectsList';
import { SubjectCreateEdit } from '../pages/subjects/SubjectCreateEdit';
import { SubjectDetails } from '../pages/subjects/SubjectDetails';
import { ExamCreateEdit } from '../pages/exams/ExamCreateEdit';
import { ExamDetails } from '../pages/exams/ExamDetails';
import { StudentsList } from '../pages/students/StudentsList';
import { StudentCreateEdit } from '../pages/students/StudentCreateEdit';
import { QuestionCreateEdit } from '../pages/exams/QuestionCreateEdit';
import { ModelAnswerCreateEdit } from '../pages/exams/ModelAnswerCreateEdit';
import { RubricCreateEdit } from '../pages/exams/RubricCreateEdit';
import { OCRResultsViewer } from '../pages/exams/OCRResultsViewer';
import { QuestionMappingViewer } from '../pages/exams/QuestionMappingViewer';
import { EvaluationDetailsViewer } from '../pages/exams/EvaluationDetailsViewer';
import { EvaluationExplanationViewer } from '../pages/exams/EvaluationExplanationViewer';
import { PlagiarismDashboard } from '../pages/plagiarism/PlagiarismDashboard';
import { PlagiarismExamSummary } from '../pages/plagiarism/PlagiarismExamSummary';
import { PlagiarismReportViewer } from '../pages/plagiarism/PlagiarismReportViewer';
import { ResultsDashboard } from '../pages/results/ResultsDashboard';
import { ExamResultsViewer } from '../pages/results/ExamResultsViewer';
import { StudentResultsViewer } from '../pages/results/StudentResultsViewer';

import { PortalShell } from '../components/layout/PortalShell';
import { SuperAdminPortal } from '../pages/portals/SuperAdminPortal';
import { AcademicAdminPortal } from '../pages/portals/AcademicAdminPortal';
import { TeacherPortal } from '../pages/portals/TeacherPortal';
import { OCRReviewPortal } from '../pages/portals/OCRReviewPortal';
import { AIEvaluationPortal } from '../pages/portals/AIEvaluationPortal';
import { EvaluatorPortal } from '../pages/portals/EvaluatorPortal';
import { IntegrityPortal } from '../pages/portals/IntegrityPortal';
import { StudentPortal } from '../pages/portals/StudentPortal';
import { AnalyticsPortal } from '../pages/portals/AnalyticsPortal';
import { ResearchLabPortal } from '../pages/portals/ResearchLabPortal';
import { StudyMateLanding } from '../pages/frontpage/StudyMateLanding';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <StudyMateLanding />,
  },
  {
    path: '/home',
    element: <StudyMateLanding />,
  },
  {
    path: '/login',
    element: (
      <PublicRoute>
        <Login />
      </PublicRoute>
    ),
  },
  {
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'subjects',
        element: <SubjectsList />,
      },
      {
        path: 'subjects/new',
        element: <SubjectCreateEdit />,
      },
      {
        path: 'subjects/:id',
        element: <SubjectDetails />,
      },
      {
        path: 'subjects/:id/edit',
        element: <SubjectCreateEdit />,
      },
      {
        path: 'subjects/:subjectId/exams/new',
        element: <ExamCreateEdit />,
      },
      {
        path: 'subjects/:subjectId/exams/:id/edit',
        element: <ExamCreateEdit />,
      },
      {
        path: 'exams/:id',
        element: <ExamDetails />,
      },
      {
        path: 'exams/:examId/questions/new',
        element: <QuestionCreateEdit />,
      },
      {
        path: 'exams/:examId/questions/:id/edit',
        element: <QuestionCreateEdit />,
      },
      {
        path: 'exams/:examId/questions/:questionId/model-answer',
        element: <ModelAnswerCreateEdit />,
      },
      {
        path: 'exams/:examId/questions/:questionId/rubric',
        element: <RubricCreateEdit />,
      },
      {
        path: 'exams/:examId/answer-sheets/:id/ocr',
        element: <OCRResultsViewer />,
      },
      {
        path: 'exams/:examId/answer-sheets/:id/mappings',
        element: <QuestionMappingViewer />,
      },
      {
        path: 'exams/:examId/answer-sheets/:sheetId/evaluations/:id',
        element: <EvaluationDetailsViewer />,
      },
      {
        path: 'exams/:examId/answer-sheets/:sheetId/evaluations/:id/explanation',
        element: <EvaluationExplanationViewer />,
      },
      {
        path: 'students',
        element: <StudentsList />,
      },
      {
        path: 'students/new',
        element: <StudentCreateEdit />,
      },
      {
        path: 'students/:id/edit',
        element: <StudentCreateEdit />,
      },
      {
        path: 'plagiarism',
        element: <PlagiarismDashboard />,
      },
      {
        path: 'plagiarism/exams/:examId',
        element: <PlagiarismExamSummary />,
      },
      {
        path: 'plagiarism/reports/:reportId',
        element: <PlagiarismReportViewer />,
      },
      {
        path: 'results',
        element: <ResultsDashboard />,
      },
      {
        path: 'results/exams/:examId',
        element: <ExamResultsViewer />,
      },
      {
        path: 'results/students/:studentId',
        element: <StudentResultsViewer />,
      },
    ],
  },
  {
    path: '/portals',
    element: (
      <ProtectedRoute>
        <PortalShell />
      </ProtectedRoute>
    ),
    children: [
      {
        path: '',
        element: <Navigate to="/portals/teacher" replace />,
      },
      {
        path: 'super-admin',
        element: <SuperAdminPortal />,
      },
      {
        path: 'academic-admin',
        element: <AcademicAdminPortal />,
      },
      {
        path: 'teacher',
        element: <TeacherPortal />,
      },
      {
        path: 'ocr-review',
        element: <OCRReviewPortal />,
      },
      {
        path: 'ai-evaluation',
        element: <AIEvaluationPortal />,
      },
      {
        path: 'evaluator',
        element: <EvaluatorPortal />,
      },
      {
        path: 'integrity',
        element: <IntegrityPortal />,
      },
      {
        path: 'student',
        element: <StudentPortal />,
      },
      {
        path: 'analytics',
        element: <AnalyticsPortal />,
      },
      {
        path: 'research-lab',
        element: <ResearchLabPortal />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
]);
